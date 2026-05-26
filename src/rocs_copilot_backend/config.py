"""Application settings.

Per spec §10: env-driven via pydantic-settings; validation runs at app startup
(failing Flask boot rather than per-request). Per §8.2 missing-API-key handling
happens in providers/llm.py, not here, because the right key depends on which
provider is selected at request time. Settings just validates LLM_PROVIDER itself.
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: Literal["groq", "openai"] = Field(...)
    openai_api_key: str | None = None
    groq_api_key: str | None = None

    openai_chat_model: str = "gpt-4o-mini"
    groq_chat_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "text-embedding-3-small"

    chroma_dir: str = "data/chroma"
    corpus_dir: str = "data/corpus"

    retrieval_min_score: float = 0.3
    retrieval_top_k: int = 4
    history_turn_cap: int = 8
