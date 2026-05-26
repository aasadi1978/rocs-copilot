"""Tests for POST /api/chat. Mocks the chain and store."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from rocs_copilot_backend.app import create_app


def _parse_sse(body: bytes) -> list[tuple[str, dict]]:
    """Parse SSE response body into (event_name, data_dict) pairs."""
    events: list[tuple[str, dict]] = []
    cur_event = None
    for line in body.decode().splitlines():
        if line.startswith("event:"):
            cur_event = line.removeprefix("event:").strip()
        elif line.startswith("data:"):
            payload = json.loads(line.removeprefix("data:").strip())
            assert cur_event is not None
            events.append((cur_event, payload))
            cur_event = None
    return events


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    app = create_app()
    return app.test_client()


def test_chat_happy_path_streams_tokens_then_source_then_done(client):
    """Spec §7.2: tokens first, then source, then done."""
    fake_events = [
        {"kind": "token", "text": "Hello "},
        {"kind": "token", "text": "world."},
        {"kind": "source", "chunks": [{"id": "m.pdf:p1", "filename": "m.pdf",
                                       "page": 1, "score": 0.8, "snippet": "..."}]},
        {"kind": "done"},
    ]

    def fake_stream(self, question, history):
        yield from fake_events

    from rocs_copilot_backend.chains import rag_chain
    with patch.object(rag_chain.RagChain, "stream", fake_stream):
        resp = client.post("/api/chat", json={"question": "hi", "history": []})

    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/event-stream")
    events = _parse_sse(resp.data)
    kinds = [name for name, _ in events]
    # Order assertions per spec §7.2: all tokens before source, source before done.
    assert kinds == ["token", "token", "source", "done"]


def test_chat_no_corpus_emits_error_event(client):
    """Spec §8.2: empty Chroma store → error code 'no_corpus'."""
    from rocs_copilot_backend.ingest.store import ChromaStore
    with patch.object(ChromaStore, "count", return_value=0):
        resp = client.post("/api/chat", json={"question": "hi", "history": []})

    events = _parse_sse(resp.data)
    assert events[0][0] == "error"
    assert events[0][1]["code"] == "no_corpus"
    assert events[-1][0] == "done"


def test_chat_retrieval_miss_streams_canned_no_source(client):
    """Spec §8.2: retrieval miss → canned answer tokens, NO source event."""
    fake_events = [
        {"kind": "token", "text": "I don't have documentation covering that. "},
        {"kind": "token", "text": "Try asking about specific error codes..."},
        {"kind": "done"},
    ]

    def fake_stream(self, question, history):
        yield from fake_events

    from rocs_copilot_backend.chains import rag_chain
    with patch.object(rag_chain.RagChain, "stream", fake_stream):
        resp = client.post("/api/chat", json={"question": "off-topic", "history": []})

    events = _parse_sse(resp.data)
    kinds = [name for name, _ in events]
    assert "source" not in kinds
    assert kinds[-1] == "done"


def test_chat_llm_unavailable_emits_error_event(client):
    """Spec §8.2: LLM provider error mid-stream → error code 'llm_unavailable'."""
    def fake_stream(self, question, history):
        yield {"kind": "token", "text": "Start "}
        raise RuntimeError("rate limited")

    from rocs_copilot_backend.chains import rag_chain
    with patch.object(rag_chain.RagChain, "stream", fake_stream):
        resp = client.post("/api/chat", json={"question": "hi", "history": []})

    events = _parse_sse(resp.data)
    error_events = [e for e in events if e[0] == "error"]
    assert len(error_events) == 1
    assert error_events[0][1]["code"] == "llm_unavailable"
    assert error_events[0][1]["retryable"] is True


def test_chat_invalid_body_returns_400(client):
    """Missing 'question' → 400 (not SSE; this is a client error)."""
    resp = client.post("/api/chat", json={"history": []})
    assert resp.status_code == 400
