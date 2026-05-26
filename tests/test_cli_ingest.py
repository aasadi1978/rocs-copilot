"""Smoke tests for the ingestion CLI. Uses fake embeddings + tmp Chroma dir."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tests.test_store import FakeEmbeddings  # reuse the deterministic fake

import scripts.ingest as ingest_cli


@pytest.fixture
def patched_dirs(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus"
    chroma = tmp_path / "chroma"
    corpus.mkdir()
    chroma.mkdir()
    monkeypatch.setenv("CORPUS_DIR", str(corpus))
    monkeypatch.setenv("CHROMA_DIR", str(chroma))
    # Copy the fixture corpus into the tmp corpus dir.
    fixtures = Path(__file__).parent / "fixtures" / "corpus"
    for f in fixtures.iterdir():
        shutil.copy(f, corpus / f.name)
    return corpus, chroma


@pytest.fixture
def fake_embeddings(monkeypatch):
    """Replace the real embeddings factory with a deterministic fake."""
    monkeypatch.setattr(ingest_cli, "get_embeddings", lambda: FakeEmbeddings())


def test_main_indexes_fixtures(patched_dirs, fake_embeddings, caplog):
    caplog.set_level("INFO")
    rc = ingest_cli.main()
    assert rc == 0
    assert "Indexed: 2 / Skipped: 0" in caplog.text


def test_main_empty_corpus_returns_1(tmp_path, monkeypatch, fake_embeddings, caplog):
    empty_corpus = tmp_path / "empty"
    empty_corpus.mkdir()
    monkeypatch.setenv("CORPUS_DIR", str(empty_corpus))
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path / "chroma"))
    caplog.set_level("ERROR")
    rc = ingest_cli.main()
    assert rc == 1
    assert "No documents found" in caplog.text


def test_main_missing_api_key_returns_2(patched_dirs, monkeypatch, caplog):
    # Real factory is in play (no fake_embeddings fixture). No OPENAI_API_KEY set.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    caplog.set_level("ERROR")
    rc = ingest_cli.main()
    assert rc == 2
    assert "Provider misconfig" in caplog.text
