"""Tests for the LLM client factory."""

from __future__ import annotations

from unittest.mock import MagicMock

from pydantic import SecretStr


def test_factory_returns_ollama_client(monkeypatch) -> None:
    """Returns OllamaClient when llm_provider is 'ollama'."""
    import app.llm as llm_module
    from app.llm.ollama_client import OllamaClient

    mock_settings = MagicMock()
    mock_settings.llm_provider = "ollama"
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_settings.ollama_model = "llama3.2:3b"

    llm_module.get_llm_client.cache_clear()
    monkeypatch.setattr("app.llm.get_settings", lambda: mock_settings)
    monkeypatch.setattr("app.llm.ollama_client.get_settings", lambda: mock_settings)

    client = llm_module.get_llm_client()
    assert isinstance(client, OllamaClient)

    llm_module.get_llm_client.cache_clear()


def test_factory_returns_claude_client(monkeypatch) -> None:
    """Returns ClaudeClient when llm_provider is 'claude'."""
    import app.llm as llm_module
    from app.llm.claude_client import ClaudeClient

    mock_settings = MagicMock()
    mock_settings.llm_provider = "claude"
    mock_settings.anthropic_api_key = SecretStr("sk-test")
    mock_settings.claude_model = "claude-haiku-4-5"

    llm_module.get_llm_client.cache_clear()
    monkeypatch.setattr("app.llm.get_settings", lambda: mock_settings)
    monkeypatch.setattr("app.llm.claude_client.get_settings", lambda: mock_settings)
    monkeypatch.setattr("app.llm.claude_client.anthropic.AsyncAnthropic", MagicMock())

    client = llm_module.get_llm_client()
    assert isinstance(client, ClaudeClient)

    llm_module.get_llm_client.cache_clear()


def test_factory_is_singleton(monkeypatch) -> None:
    """get_llm_client() returns the same instance on repeated calls."""
    import app.llm as llm_module

    mock_settings = MagicMock()
    mock_settings.llm_provider = "ollama"
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_settings.ollama_model = "llama3.2:3b"

    llm_module.get_llm_client.cache_clear()
    monkeypatch.setattr("app.llm.get_settings", lambda: mock_settings)
    monkeypatch.setattr("app.llm.ollama_client.get_settings", lambda: mock_settings)

    client1 = llm_module.get_llm_client()
    client2 = llm_module.get_llm_client()
    assert client1 is client2

    llm_module.get_llm_client.cache_clear()
