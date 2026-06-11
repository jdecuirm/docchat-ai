"""Ollama LLM client — streams tokens via the Ollama HTTP API.

Ollama's ``/api/generate`` endpoint returns newline-delimited JSON (NDJSON).
Each line is ``{"response": "<token>", "done": false}``; the final line has
``"done": true`` and an empty ``"response"``.
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from app.config import get_settings
from app.llm.base import BaseLLMClient

__all__ = ["OllamaClient"]

_TIMEOUT = 120.0  # seconds — models can be slow on cold start


class OllamaClient(BaseLLMClient):
    """LLM client backed by a local Ollama server.

    Reads ``OLLAMA_BASE_URL`` and ``OLLAMA_MODEL`` from settings.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream tokens from Ollama's /api/generate endpoint.

        Args:
            prompt: Fully-assembled prompt string.

        Yields:
            Non-empty text tokens as they arrive from Ollama.

        Raises:
            httpx.HTTPStatusError: If Ollama returns a non-2xx status code.
        """
        url = f"{self._base_url}/api/generate"
        async with httpx.AsyncClient(timeout=_TIMEOUT) as http:
            async with http.stream(
                "POST",
                url,
                json={"model": self._model, "prompt": prompt, "stream": True},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if token := data.get("response"):
                            yield token
