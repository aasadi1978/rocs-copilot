"""Tests for the Chroma store wrapper. Uses tmp_path + fake embeddings."""
from __future__ import annotations

import hashlib

import pytest

from rocs_copilot_backend.ingest.store import (
    ChromaStore,
    compute_content_hash,
)


class FakeEmbeddings:
    """Deterministic embedding: 1536-dim vector of hash-derived floats."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)

    def _vec(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).digest()
        # Repeat to 1536 dims; values in [-1, 1].
        return [((b / 255.0) * 2.0) - 1.0 for b in (h * 48)[:1536]]


@pytest.fixture
def store(tmp_path):
    return ChromaStore(
        persist_dir=str(tmp_path / "chroma"),
        embeddings=FakeEmbeddings(),
    )


def test_compute_content_hash_is_deterministic():
    h1 = compute_content_hash("hello world")
    h2 = compute_content_hash("hello world")
    h3 = compute_content_hash("hello world!")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64  # sha256 hex


def test_upsert_then_retrieve(store):
    store.upsert_chunks(
        source="manual.pdf",
        page=1,
        chunks=["Sample text about routing.", "Another chunk about errors."],
    )
    results = store.similarity_search("routing", k=2)
    assert len(results) == 2
    # Both chunks should be retrieved; ordering depends on similarity.
    texts = {r["text"] for r in results}
    assert texts == {"Sample text about routing.", "Another chunk about errors."}


def test_upsert_is_idempotent(store):
    """Spec §6.1: content-hash idempotency. Re-ingesting same source+content adds no duplicates."""
    chunks = ["Sample text about routing.", "Another chunk about errors."]
    store.upsert_chunks(source="manual.pdf", page=1, chunks=chunks)
    store.upsert_chunks(source="manual.pdf", page=1, chunks=chunks)  # re-run
    results = store.similarity_search("routing", k=10)
    assert len(results) == 2  # not 4


def test_similarity_search_returns_metadata(store):
    store.upsert_chunks(source="manual.pdf", page=7, chunks=["Routing details."])
    results = store.similarity_search("routing", k=1)
    assert results[0]["source"] == "manual.pdf"
    assert results[0]["page"] == 7
    assert "score" in results[0]
    assert "text" in results[0]


def test_count_returns_zero_for_empty_store(store):
    assert store.count() == 0


def test_count_returns_total_chunks(store):
    store.upsert_chunks(source="a.pdf", page=1, chunks=["one", "two"])
    store.upsert_chunks(source="b.pdf", page=1, chunks=["three"])
    assert store.count() == 3
