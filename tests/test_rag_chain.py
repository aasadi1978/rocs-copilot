"""Tests for the RAG chain. Mocks the LLM and the store; verifies orchestration."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from rocs_copilot_backend.chains.rag_chain import build_chain, rewrite_question


class FakeChatModel:
    """Records calls and returns a canned response."""

    def __init__(self, response: str = "REWRITTEN") -> None:
        self.calls: list[str] = []
        self._response = response

    def invoke(self, messages, **_):
        captured = "\n".join(getattr(m, "content", str(m)) for m in messages)
        self.calls.append(captured)
        from langchain_core.messages import AIMessage
        return AIMessage(content=self._response)


def test_rewrite_question_no_history_returns_input():
    """No prior turns → standalone query == original question."""
    llm = FakeChatModel(response="ignored")
    out = rewrite_question(llm, question="What is error SAMPLE-001?", history=[])
    assert out == "What is error SAMPLE-001?"
    assert llm.calls == []  # short-circuit: no LLM call when history is empty


def test_rewrite_question_with_history_invokes_llm():
    """Prior turns → LLM is asked to rewrite into a standalone query."""
    llm = FakeChatModel(response="What is error SAMPLE-001?")
    history = [
        {"role": "user", "content": "Tell me about routing errors."},
        {"role": "assistant", "content": "There are several. SAMPLE-001 is..."},
    ]
    out = rewrite_question(llm, question="Tell me more about that one.", history=history)
    assert out == "What is error SAMPLE-001?"
    assert len(llm.calls) == 1


def test_build_chain_returns_callable():
    """Composition smoke: chain is callable with (question, history)."""
    llm = FakeChatModel(response="Sample answer about SAMPLE-001.")

    class FakeStore:
        def similarity_search(self, query, k):
            return [
                {"text": "SAMPLE-001 means routing failed.", "source": "manual.pdf",
                 "page": 1, "score": 0.8},
            ]

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    assert callable(chain.stream)


def test_chain_stream_yields_answer_then_sources():
    """Spec §7.2: emits answer tokens, then a 'sources' marker, then done."""
    llm = MagicMock()
    from langchain_core.messages import AIMessageChunk

    llm.stream = MagicMock(return_value=iter([
        AIMessageChunk(content="Based "),
        AIMessageChunk(content="on the manual, "),
        AIMessageChunk(content="SAMPLE-001 means..."),
    ]))
    llm.invoke = MagicMock(return_value=AIMessageChunk(content="standalone"))

    class FakeStore:
        def similarity_search(self, query, k):
            return [
                {"text": "...", "source": "manual.pdf", "page": 1, "score": 0.8},
            ]

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    events = list(chain.stream(question="What is SAMPLE-001?", history=[]))

    # Expect: 3 token events, 1 source event, 1 done event.
    kinds = [e["kind"] for e in events]
    assert kinds.count("token") == 3
    assert kinds.count("source") == 1
    assert kinds.count("done") == 1
    # Order: all tokens before source, source before done (spec §7.2).
    assert kinds.index("source") > max(i for i, k in enumerate(kinds) if k == "token")
    assert kinds.index("done") == len(kinds) - 1


def test_chain_stream_retrieval_miss_yields_canned_answer_no_source():
    """Spec §8.2: best score < min_score → canned response, no LLM call, no source event."""
    llm = MagicMock()
    llm.stream = MagicMock(side_effect=AssertionError("LLM should NOT be called on retrieval miss"))

    class FakeStore:
        def similarity_search(self, query, k):
            return [{"text": "irrelevant", "source": "x.pdf", "page": 1, "score": 0.1}]

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    events = list(chain.stream(question="totally off-topic", history=[]))

    kinds = [e["kind"] for e in events]
    assert "source" not in kinds  # no source event on miss
    assert kinds[-1] == "done"
    full_text = "".join(e["text"] for e in events if e["kind"] == "token")
    assert "I don't have documentation covering that" in full_text


def test_chain_stream_no_hits_yields_canned_answer():
    """Empty retrieval → same canned response as score-below-threshold."""
    llm = MagicMock()
    llm.stream = MagicMock(side_effect=AssertionError("LLM should NOT be called"))

    class FakeStore:
        def similarity_search(self, query, k):
            return []

    chain = build_chain(llm=llm, store=FakeStore(), min_score=0.3, top_k=4)
    events = list(chain.stream(question="anything", history=[]))
    full_text = "".join(e["text"] for e in events if e["kind"] == "token")
    assert "I don't have documentation covering that" in full_text
