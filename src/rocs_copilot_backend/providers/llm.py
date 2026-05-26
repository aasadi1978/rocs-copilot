"""LLM + embeddings provider factory. Branches on LLM_PROVIDER env var.

Per spec §4 + §6.1: provider abstraction is load-bearing because FedEx prod GCP
has no programmatic LLM today. Dev supports openai + groq; embeddings always
OpenAI in MVP.
"""
from __future__ import annotations

import os
from typing import Any


def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise ValueError(f"{name} is required in environment")
    return val


def get_chat_model() -> Any:
    """Return a LangChain chat model instance based on LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER")
    if not provider:
        raise ValueError("LLM_PROVIDER is required in environment (groq | openai)")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = _require_env("OPENAI_API_KEY")
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, api_key=api_key, streaming=True)

    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = _require_env("GROQ_API_KEY")
        model = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model, api_key=api_key, streaming=True)

    raise ValueError(
        f"Unknown LLM_PROVIDER={provider!r}. Supported: groq, openai."
    )


def get_embeddings() -> Any:
    """Return a LangChain embeddings instance.

    Per spec §10: embeddings always use OpenAI in MVP, regardless of LLM_PROVIDER.
    """
    from langchain_openai import OpenAIEmbeddings

    api_key = _require_env("OPENAI_API_KEY")
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model, api_key=api_key)
