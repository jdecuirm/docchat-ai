"""Unit tests for OllamaClient — no real Ollama server required."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_httpx_mock(ndjson_lines: list[str]) -> MagicMock:
    """Build a mock httpx.AsyncClient that streams the given NDJSON lines."""

    async def aiter_lines():
        for line in ndjson_lines:
            yield line

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.aiter_lines = aiter_lines

    mock_response_cm = AsyncMock()
    mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response_cm.__aexit__ = AsyncMock(return_value=None)

    mock_http = MagicMock()
    mock_http.stream = MagicMock(return_value=mock_response_cm)

    mock_client_cm = AsyncMock()
    mock_client_cm.__aenter__ = AsyncMock(return_value=mock_http)
    mock_client_cm.__aexit__ = AsyncMock(return_value=None)

    return mock_client_cm


async def test_generate_yields_tokens(monkeypatch) -> None:
    """Tokens from NDJSON lines are yielded in order."""
    from app.llm.ollama_client import OllamaClient

    lines = [
        '{"response": "Hello", "done": false}',
        '{"response": " world", "done": false}',
        '{"response": "", "done": true}',
    ]
    monkeypatch.setattr(
        "app.llm.ollama_client.httpx.AsyncClient",
        lambda **_: _make_httpx_mock(lines),
    )

    client = OllamaClient()
    tokens = [t async for t in client.generate("test prompt")]

    assert tokens == ["Hello", " world"]


async def test_generate_skips_empty_response(monkeypatch) -> None:
    """Lines where 'response' is empty string are not yielded."""
    from app.llm.ollama_client import OllamaClient

    lines = [
        '{"response": "Hi", "done": false}',
        '{"response": "", "done": false}',
        '{"response": "!", "done": false}',
        '{"response": "", "done": true}',
    ]
    monkeypatch.setattr(
        "app.llm.ollama_client.httpx.AsyncClient",
        lambda **_: _make_httpx_mock(lines),
    )

    client = OllamaClient()
    tokens = [t async for t in client.generate("test prompt")]

    assert tokens == ["Hi", "!"]


async def test_generate_skips_blank_lines(monkeypatch) -> None:
    """Blank lines in the stream are ignored without raising."""
    from app.llm.ollama_client import OllamaClient

    lines = [
        "",
        '{"response": "token", "done": false}',
        "",
        '{"response": "", "done": true}',
    ]
    monkeypatch.setattr(
        "app.llm.ollama_client.httpx.AsyncClient",
        lambda **_: _make_httpx_mock(lines),
    )

    client = OllamaClient()
    tokens = [t async for t in client.generate("test prompt")]

    assert tokens == ["token"]


async def test_generate_raises_on_http_error(monkeypatch) -> None:
    """Non-2xx response propagates as httpx.HTTPStatusError."""
    import httpx
    from app.llm.ollama_client import OllamaClient

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(),
        )
    )
    mock_response.aiter_lines = AsyncMock()

    mock_response_cm = AsyncMock()
    mock_response_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response_cm.__aexit__ = AsyncMock(return_value=None)

    mock_http = MagicMock()
    mock_http.stream = MagicMock(return_value=mock_response_cm)

    mock_client_cm = AsyncMock()
    mock_client_cm.__aenter__ = AsyncMock(return_value=mock_http)
    mock_client_cm.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr(
        "app.llm.ollama_client.httpx.AsyncClient",
        lambda **_: mock_client_cm,
    )

    client = OllamaClient()
    with pytest.raises(httpx.HTTPStatusError):
        async for _ in client.generate("test prompt"):
            pass
