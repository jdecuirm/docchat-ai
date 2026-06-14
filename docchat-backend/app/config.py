"""Application configuration loaded from environment variables.

Settings are read from a local ``.env`` file (see ``.env.example``) or the
process environment via ``pydantic-settings``. Import the shared, cached
instance with :func:`get_settings` so the environment is parsed only once.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources.base import PydanticBaseSettingsSource
from pydantic_settings.sources.providers.dotenv import DotEnvSettingsSource


class _TolerantDotEnvSource(DotEnvSettingsSource):
    """DotEnvSettingsSource that accepts comma-separated strings for list fields.

    pydantic-settings 2.x calls ``json.loads`` on list-typed fields from the
    .env file before Pydantic field validators run.  This crashes when the
    value is a comma-separated string (e.g. ``http://a,http://b``).  This
    subclass falls back to returning the raw string on ``JSONDecodeError`` so
    the Pydantic model validator can handle it.
    """

    def decode_complex_value(
        self, field_name: str, field: FieldInfo, value: Any
    ) -> Any:
        """Try JSON decode; on failure return raw value for validator handling."""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


class Settings(BaseSettings):
    """Runtime configuration for the DocChat AI backend.

    Every field maps to an upper-cased environment variable of the same name
    (e.g. ``llm_provider`` -> ``LLM_PROVIDER``). Defaults match the values
    documented in the project ``CLAUDE.md`` so the service runs locally with
    Ollama out of the box.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM provider --------------------------------------------------------
    llm_provider: Literal["ollama", "claude"] = "ollama"

    # Ollama (local development).
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # Claude (demo / production). The API key is only required when
    # ``llm_provider`` is ``"claude"``.
    anthropic_api_key: SecretStr | None = None
    claude_model: str = "claude-haiku-4-5"

    # --- Embeddings & re-ranking ---------------------------------------------
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"

    # --- Vector store --------------------------------------------------------
    chroma_persist_dir: str = "./chroma_data"

    # --- Chunking ------------------------------------------------------------
    chunk_size: int = 256
    chunk_overlap: int = 30

    # --- Retrieval -----------------------------------------------------------
    top_k_retrieval: int = 15
    top_k_rerank: int = 4

    # --- API / CORS ----------------------------------------------------------
    cors_allow_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Parse a comma-separated string into a list of origins."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Replace the default DotEnvSettingsSource with the tolerant variant."""
        tolerant_dotenv = _TolerantDotEnvSource(settings_cls)
        return init_settings, env_settings, tolerant_dotenv, file_secret_settings


@lru_cache
def get_settings() -> Settings:
    """Return the cached :class:`Settings` instance for the process."""
    return Settings()
