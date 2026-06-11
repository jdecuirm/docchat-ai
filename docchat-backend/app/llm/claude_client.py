"""Claude LLM client — streams tokens via the Anthropic SDK.

Uses ``AsyncAnthropic.messages.stream()`` for server-sent events streaming.
Requires ``ANTHROPIC_API_KEY`` in the environment when ``LLM_PROVIDER=claude``.
"""

from __future__ import annotations

from typing import AsyncGenerator

import anthropic

from app.config import get_settings
from app.llm.base import BaseLLMClient

__all__ = ["ClaudeClient"]

_MAX_TOKENS = 1024


class ClaudeClient(BaseLLMClient):
    """LLM client backed by the Anthropic Claude API.

    Reads ``ANTHROPIC_API_KEY`` and ``CLAUDE_MODEL`` from settings.
    Raises :class:`ValueError` at construction time if the API key is absent.
    """

    def __init__(self) -> None:
        settings = get_settings()
        if settings.anthropic_api_key is None:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=claude. "
                "Set it in your .env file."
            )
        self._client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key.get_secret_value()
        )
        self._model = settings.claude_model

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream tokens from the Claude API.

        Args:
            prompt: Fully-assembled prompt string.

        Yields:
            Text tokens as they arrive from the Claude API.
        """
        async with self._client.messages.stream(
            model=self._model,
            max_tokens=_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
