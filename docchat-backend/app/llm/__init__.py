"""LLM abstraction layer — provider-switchable via LLM_PROVIDER env var.

Usage::

    from app.llm import get_llm_client

    client = get_llm_client()
    async for token in client.generate(prompt):
        yield token

Changing providers requires only setting ``LLM_PROVIDER=claude`` (or ``ollama``)
in the environment. No code changes needed.
"""

from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.llm.base import BaseLLMClient
from app.llm.claude_client import ClaudeClient
from app.llm.ollama_client import OllamaClient

__all__ = ["get_llm_client"]


@lru_cache(maxsize=1)
def get_llm_client() -> BaseLLMClient:
    """Return the configured LLM client singleton.

    Reads ``LLM_PROVIDER`` from settings and returns the matching client:

    - ``"ollama"`` → :class:`OllamaClient` (default, local development)
    - ``"claude"`` → :class:`ClaudeClient` (demo / production)

    Returns:
        The cached :class:`BaseLLMClient` instance for the process.
    """
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaClient()
    return ClaudeClient()
