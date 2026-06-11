"""Abstract base class for LLM provider clients.

All provider implementations must subclass :class:`BaseLLMClient` and
implement :meth:`generate`. Use :func:`app.llm.get_llm_client` to obtain
the configured singleton — callers never import provider classes directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator

__all__ = ["BaseLLMClient"]


class BaseLLMClient(ABC):
    """Common interface for all LLM provider clients.

    Subclasses implement :meth:`generate` as an async generator that yields
    text tokens one at a time, enabling streaming responses in FastAPI.
    """

    @abstractmethod
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream a completion for the given prompt.

        Args:
            prompt: The fully-assembled prompt string. The RAG pipeline
                (Stage F) is responsible for building this from context
                chunks and the user query. This client has no knowledge
                of RAG structure.

        Yields:
            Text tokens as they arrive from the LLM provider.
        """
