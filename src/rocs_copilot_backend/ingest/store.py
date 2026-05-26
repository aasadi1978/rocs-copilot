"""Chroma store wrapper with content-hash idempotency.

Per spec §6.1: re-running ingest on the same source file produces no duplicates.
Embeddings are injected (DI) so the call site decides which provider to use and
tests can substitute a fake.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma

COLLECTION_NAME = "rocs_copilot"


def compute_content_hash(text: str) -> str:
    """Stable sha256 hex of the chunk text. Used as the Chroma document ID."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ChromaStore:
    """Thin wrapper around langchain_chroma.Chroma with idempotent upserts."""

    def __init__(self, persist_dir: str, embeddings: Any) -> None:
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )

    def upsert_chunks(
        self,
        source: str,
        page: int,
        chunks: list[str],
    ) -> None:
        """Upsert chunks with content-hash IDs. Re-upserting same text is a no-op."""
        if not chunks:
            return
        ids = [compute_content_hash(c) for c in chunks]
        metadatas = [{"source": source, "page": page} for _ in chunks]
        # Use the underlying chromadb collection's upsert directly to guarantee
        # idempotency: add() raises on duplicate IDs; upsert() silently overwrites.
        self._client._collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=self._client._embedding_function.embed_documents(chunks),
        )

    def similarity_search(self, query: str, k: int = 4) -> list[dict]:
        """Return top-k hits with text + metadata + cosine similarity score (0..1)."""
        # similarity_search_with_relevance_scores returns a relevance score in [0,1]
        # (1 = identical, 0 = unrelated) — what we want for §8.2 threshold checks.
        hits = self._client.similarity_search_with_relevance_scores(query, k=k)
        return [
            {
                "text": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "page": doc.metadata.get("page", 0),
                "score": float(score),
            }
            for doc, score in hits
        ]

    def count(self) -> int:
        """Total number of vectors in the collection."""
        return self._client._collection.count()
