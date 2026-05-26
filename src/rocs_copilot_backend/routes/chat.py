"""POST /api/chat — SSE streaming. Wraps the RAG chain output.

Spec references:
  - §7.1 request shape: {"question": str, "history": [{"role","content"}]}
  - §7.2 ordering: tokens → source → done
  - §8.2 error codes: no_corpus, llm_unavailable, internal (all 'retryable' bool)
"""
from __future__ import annotations

import json
import logging
from typing import Iterator

from flask import Blueprint, Response, current_app, request

log = logging.getLogger(__name__)

bp = Blueprint("chat", __name__, url_prefix="/api")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _generate(
    question: str,
    history: list[dict],
) -> Iterator[str]:
    chain = current_app.extensions["rag_chain"]
    store = current_app.extensions["chroma_store"]

    # §8.2: empty corpus check
    try:
        if store.count() == 0:
            yield _sse("error", {
                "code": "no_corpus",
                "message": "No documents indexed yet. Run scripts/ingest.py first.",
                "retryable": False,
            })
            yield _sse("done", {})
            return
    except Exception:
        log.exception("corpus count failed")
        yield _sse("error", {
            "code": "internal",
            "message": "Something went wrong on our end.",
            "retryable": True,
        })
        yield _sse("done", {})
        return

    try:
        for event in chain.stream(question=question, history=history):
            kind = event["kind"]
            if kind == "token":
                yield _sse("token", {"text": event["text"]})
            elif kind == "source":
                yield _sse("source", {"chunks": event["chunks"]})
            elif kind == "done":
                yield _sse("done", {})
    except GeneratorExit:
        log.info("client disconnected")
        raise
    except Exception:
        log.exception("LLM provider error")
        yield _sse("error", {
            "code": "llm_unavailable",
            "message": "The assistant is temporarily unavailable. Please try again in a moment.",
            "retryable": True,
        })
        yield _sse("done", {})


@bp.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    question = body.get("question")
    history = body.get("history", [])
    if not question or not isinstance(question, str):
        return ({"error": "missing or invalid 'question'"}, 400)

    return Response(
        _generate(question, history),
        mimetype="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
