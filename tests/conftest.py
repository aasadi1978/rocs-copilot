import os
import pytest


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    for var in (
        "LLM_PROVIDER", "OPENAI_API_KEY", "GROQ_API_KEY",
        "OPENAI_CHAT_MODEL", "GROQ_CHAT_MODEL", "EMBEDDING_MODEL",
        "CHROMA_DIR", "CORPUS_DIR",
        "RETRIEVAL_MIN_SCORE", "RETRIEVAL_TOP_K", "HISTORY_TURN_CAP",
    ):
        monkeypatch.delenv(var, raising=False)
