"""RAG chain: history-aware retriever → LLM → token stream.

Per spec §7.3:
  1. If history non-empty, LLM rewrites the question into a standalone query.
  2. Standalone query → Chroma similarity_search (top_k).
  3. If best score < min_score (or zero hits): yield canned no-docs answer; skip LLM.
  4. Otherwise: stream LLM answer tokens, then emit one source event, then done.

Per spec §7.2: ordering is TOKENS → SOURCE → DONE.
"""
from __future__ import annotations

from typing import Any, Iterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

NO_DOCS_MESSAGE = (
    "I don't have documentation covering that. "
    "Try asking about specific error codes, ROCS modules, or operational procedures."
)

REWRITE_SYSTEM = (
    "You are a query rewriter. Given a chat history and a new user question, "
    "rewrite the new question as a fully standalone query that captures the user's "
    "intent without needing the prior turns to interpret. If the new question is "
    "already standalone, return it unchanged. Output ONLY the rewritten question."
)

ANSWER_SYSTEM = (
    "You are a helpful assistant for FedEx ROCS planners. Answer the user's question "
    "using ONLY the provided context. If the context is insufficient, say so. Cite the "
    "source documents inline using their filenames when helpful."
)


def rewrite_question(llm: Any, question: str, history: list[dict]) -> str:
    """Rewrite a follow-up question into a standalone retrieval query.

    Short-circuits when history is empty (saves a round-trip).
    """
    if not history:
        return question
    history_text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
    messages = [
        SystemMessage(content=REWRITE_SYSTEM),
        HumanMessage(content=f"Chat history:\n{history_text}\n\nNew question: {question}"),
    ]
    result = llm.invoke(messages)
    return result.content.strip()


def _format_context(hits: list[dict]) -> str:
    return "\n\n".join(
        f"[{h['source']} p.{h['page']}] {h['text']}" for h in hits
    )


def _format_history_messages(history: list[dict]) -> list[Any]:
    out: list[Any] = []
    for turn in history:
        if turn["role"] == "user":
            out.append(HumanMessage(content=turn["content"]))
        else:
            out.append(AIMessage(content=turn["content"]))
    return out


class RagChain:
    def __init__(self, llm: Any, store: Any, min_score: float, top_k: int) -> None:
        self._llm = llm
        self._store = store
        self._min_score = min_score
        self._top_k = top_k

    def stream(self, question: str, history: list[dict]) -> Iterator[dict]:
        # §8.2: empty corpus guard — check before any LLM calls.
        # Uses getattr so that test double stores without count() still work.
        count_fn = getattr(self._store, "count", None)
        if count_fn is not None and count_fn() == 0:
            yield {"kind": "error", "code": "no_corpus",
                   "message": "No documents indexed yet. Run scripts/ingest.py first.",
                   "retryable": False}
            yield {"kind": "done"}
            return

        # Step 1: rewrite for retrieval
        query = rewrite_question(self._llm, question, history)

        # Step 2: retrieve
        hits = self._store.similarity_search(query, k=self._top_k)

        # Step 3: retrieval-miss → canned answer, NO LLM call, NO source event
        if not hits or hits[0]["score"] < self._min_score:
            for word in NO_DOCS_MESSAGE.split(" "):
                yield {"kind": "token", "text": word + " "}
            yield {"kind": "done"}
            return

        # Step 4: stream LLM answer, then emit source event, then done
        context = _format_context(hits)
        messages = [
            SystemMessage(content=ANSWER_SYSTEM),
            *_format_history_messages(history),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]
        for chunk in self._llm.stream(messages):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield {"kind": "token", "text": text}

        yield {
            "kind": "source",
            "chunks": [
                {
                    "id": f"{h['source']}:p{h['page']}",
                    "filename": h["source"],
                    "page": h["page"],
                    "score": round(h["score"], 4),
                    "snippet": h["text"][:200],
                }
                for h in hits
            ],
        }
        yield {"kind": "done"}


def build_chain(llm: Any, store: Any, min_score: float, top_k: int) -> RagChain:
    return RagChain(llm=llm, store=store, min_score=min_score, top_k=top_k)
