"""Unit tests for ClaudeClient — no real Anthropic API key required."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr


@pytest.fixture()
def mock_settings(monkeypatch):
    """Patch get_settings in claude_client to return a fake settings object."""
    settings = MagicMock()
    settings.anthropic_api_key = SecretStr("sk-test-key")
    settings.claude_model = "claude-haiku-4-5"
    monkeypatch.setattr("app.llm.claude_client.get_settings", lambda: settings)
    return settings


@pytest.fixture()
def mock_anthropic(monkeypatch):
    """Patch anthropic.AsyncAnthropic to return a controllable mock."""
    mock_client = MagicMock()
    monkeypatch.setattr(
        "app.llm.claude_client.anthropic.AsyncAnthropic",
        lambda api_key: mock_client,
    )
    return mock_client


def _make_stream_mock(texts: list[str]) -> MagicMock:
    """Build a mock for the anthropic messages.stream() context manager."""

    async def text_stream_gen():
        for text in texts:
            yield text

    mock_stream = MagicMock()
    mock_stream.text_stream = text_stream_gen()
    mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
    mock_stream.__aexit__ = AsyncMock(return_value=None)
    return mock_stream


async def test_generate_yields_tokens(mock_settings, mock_anthropic) -> None:
    """Tokens from text_stream are yielded in order."""
    from app.llm.claude_client import ClaudeClient

    mock_anthropic.messages.stream.return_value = _make_stream_mock(["Hello", " world"])

    client = ClaudeClient()
    tokens = [t async for t in client.generate("test prompt")]

    assert tokens == ["Hello", " world"]


async def test_generate_uses_correct_model(mock_settings, mock_anthropic) -> None:
    """generate() calls messages.stream() with the configured model."""
    from app.llm.claude_client import ClaudeClient

    mock_anthropic.messages.stream.return_value = _make_stream_mock([])

    client = ClaudeClient()
    _ = [t async for t in client.generate("test prompt")]

    call_kwargs = mock_anthropic.messages.stream.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5"


async def test_generate_uses_max_tokens_1024(mock_settings, mock_anthropic) -> None:
    """generate() passes max_tokens=1024 to the API."""
    from app.llm.claude_client import ClaudeClient

    mock_anthropic.messages.stream.return_value = _make_stream_mock([])

    client = ClaudeClient()
    _ = [t async for t in client.generate("test prompt")]

    call_kwargs = mock_anthropic.messages.stream.call_args.kwargs
    assert call_kwargs["max_tokens"] == 1024


def test_init_raises_when_api_key_missing(monkeypatch) -> None:
    """ClaudeClient raises ValueError when anthropic_api_key is None."""
    from app.llm.claude_client import ClaudeClient

    settings = MagicMock()
    settings.anthropic_api_key = None
    monkeypatch.setattr("app.llm.claude_client.get_settings", lambda: settings)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        ClaudeClient()
