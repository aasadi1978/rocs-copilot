import pytest

from rocs_copilot_backend.providers import llm as factory


def test_get_chat_model_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    model = factory.get_chat_model()
    # Class name check is enough to confirm we got the OpenAI branch.
    assert model.__class__.__name__ == "ChatOpenAI"


def test_get_chat_model_groq(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    model = factory.get_chat_model()
    assert model.__class__.__name__ == "ChatGroq"


def test_get_chat_model_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        factory.get_chat_model()


def test_get_chat_model_missing_provider_raises(monkeypatch):
    # LLM_PROVIDER not set
    with pytest.raises(ValueError, match="LLM_PROVIDER is required"):
        factory.get_chat_model()


def test_get_chat_model_openai_missing_api_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    # OPENAI_API_KEY not set
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        factory.get_chat_model()


def test_get_chat_model_groq_missing_api_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    # GROQ_API_KEY not set
    with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
        factory.get_chat_model()


def test_get_embeddings_always_openai(monkeypatch):
    """Spec §10: embeddings always use OpenAI in MVP regardless of LLM_PROVIDER."""
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")  # still required for embeddings
    emb = factory.get_embeddings()
    assert emb.__class__.__name__ == "OpenAIEmbeddings"


def test_get_embeddings_missing_openai_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-fake")
    # OPENAI_API_KEY not set
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        factory.get_embeddings()
