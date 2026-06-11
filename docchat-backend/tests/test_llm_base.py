"""Tests for the BaseLLMClient abstract base class."""

from __future__ import annotations

import pytest


def test_base_client_cannot_be_instantiated() -> None:
    """BaseLLMClient raises TypeError when instantiated directly."""
    from app.llm.base import BaseLLMClient

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseLLMClient()  # type: ignore[abstract]


def test_subclass_without_generate_cannot_be_instantiated() -> None:
    """A subclass that omits generate() raises TypeError on instantiation."""
    from app.llm.base import BaseLLMClient

    class IncompleteClient(BaseLLMClient):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteClient()  # type: ignore[abstract]


def test_concrete_subclass_satisfies_abc() -> None:
    """A subclass that implements generate() can be instantiated."""
    from app.llm.base import BaseLLMClient
    from typing import AsyncGenerator

    class ConcreteClient(BaseLLMClient):
        async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
            yield "token"

    client = ConcreteClient()
    assert isinstance(client, BaseLLMClient)
