"""Ingestion CLI.

Walks CORPUS_DIR, parses PDFs/DOCX, chunks, embeds, upserts into Chroma.
- Per-file parse failures: log + skip + continue (spec §8.1).
- Missing API keys / Chroma errors: fail loud, non-zero exit (spec §8.1).
- Embeddings API failures: tenacity backoff 3 attempts at 1s / 4s / 16s.

Usage:
    .venv/Scripts/python.exe scripts/ingest.py
    .venv/Scripts/python.exe -m scripts.ingest
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from rocs_copilot_backend.ingest.chunker import split_text
from rocs_copilot_backend.ingest.loader import LoaderError, iter_corpus, load_file
from rocs_copilot_backend.ingest.store import ChromaStore
from rocs_copilot_backend.providers.llm import get_embeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
log = logging.getLogger("ingest")


# Embeddings call wrapped with tenacity: 3 attempts at ~1s, 4s, 16s.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _upsert_with_retry(store: ChromaStore, source: str, page: int, chunks: list[str]) -> None:
    store.upsert_chunks(source=source, page=page, chunks=chunks)


def _resolve_corpus_dir() -> Path:
    raw = os.getenv("CORPUS_DIR", "data/corpus")
    return Path(raw).resolve()


def _resolve_chroma_dir() -> Path:
    raw = os.getenv("CHROMA_DIR", "data/chroma")
    return Path(raw).resolve()


def main() -> int:
    load_dotenv()  # picks up .env if present

    corpus_dir = _resolve_corpus_dir()
    if not corpus_dir.exists() or not any(corpus_dir.iterdir()):
        log.error(
            "No documents found in %s. Drop PDFs/DOCX there and rerun.",
            corpus_dir,
        )
        return 1

    try:
        embeddings = get_embeddings()  # raises ValueError on missing API key (fail loud)
    except ValueError as e:
        log.error("Provider misconfig: %s", e)
        return 2

    try:
        store = ChromaStore(persist_dir=str(_resolve_chroma_dir()), embeddings=embeddings)
    except Exception as e:
        log.error("Failed to open Chroma store: %s", e)
        return 3

    indexed = 0
    skipped = 0
    for path in iter_corpus(corpus_dir):
        try:
            pages = load_file(path)
        except LoaderError as e:
            log.warning("skipped %s: %s", path.name, e)
            skipped += 1
            continue

        for text, meta in pages:
            chunks = split_text(text)
            if not chunks:
                continue
            try:
                _upsert_with_retry(
                    store, source=meta["source"], page=meta["page"], chunks=chunks
                )
            except Exception as e:
                log.error(
                    "Failed to upsert %s page %s after retries: %s",
                    meta["source"], meta["page"], e,
                )
                return 4
        indexed += 1
        log.info("indexed %s", path.name)

    log.info("Indexed: %d / Skipped: %d", indexed, skipped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
