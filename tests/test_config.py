import pytest
from pydantic import ValidationError

from rocs_copilot_backend.config import Settings


def test_settings_loads_with_defaults(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    s = Settings()
    assert s.llm_provider == "openai"
    assert s.retrieval_min_score == 0.3
    assert s.retrieval_top_k == 4
    assert s.history_turn_cap == 8
    assert s.chroma_dir == "data/chroma"
    assert s.corpus_dir == "data/corpus"
    assert s.embedding_model == "text-embedding-3-small"


def test_settings_requires_llm_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    with pytest.raises(ValidationError):
        Settings()


def test_settings_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    with pytest.raises(ValidationError):
        Settings()


def test_settings_overrides_via_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.5")
    monkeypatch.setenv("RETRIEVAL_TOP_K", "8")
    s = Settings()
    assert s.retrieval_min_score == 0.5
    assert s.retrieval_top_k == 8
