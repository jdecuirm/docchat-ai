"""Tests for the chat streaming endpoint."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture()
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


async def test_chat_stream_yields_tokens(async_client, monkeypatch) -> None:
    """POST /chat/stream yields SSE data events for each LLM token."""
    import app.rag.pipeline as pipeline_module

    async def fake_generate(prompt: str):
        yield "Hello"
        yield " world"

    mock_client = MagicMock()
    mock_client.generate = fake_generate

    monkeypatch.setattr(pipeline_module, "retrieve", lambda q: [])
    monkeypatch.setattr(pipeline_module, "get_llm_client", lambda: mock_client)

    response = await async_client.post("/chat/stream", json={"question": "Test?"})

    assert response.status_code == 200
    text = response.text
    assert "data: Hello" in text
    assert "data:  world" in text


async def test_chat_stream_ends_with_citations(async_client, monkeypatch) -> None:
    """POST /chat/stream ends with an SSE citations event containing valid JSON."""
    import app.rag.pipeline as pipeline_module
    from app.retrieval.reranker import RankedChunk

    mock_chunks = [
        RankedChunk(
            text="Paris is the capital.",
            source_filename="doc.pdf",
            page_number=1,
            chunk_index=1,
            relevance_score=0.9,
        )
    ]

    async def fake_generate(prompt: str):
        yield "Paris."

    mock_client = MagicMock()
    mock_client.generate = fake_generate

    monkeypatch.setattr(pipeline_module, "retrieve", lambda q: mock_chunks)
    monkeypatch.setattr(pipeline_module, "get_llm_client", lambda: mock_client)

    response = await async_client.post("/chat/stream", json={"question": "Capital?"})
    text = response.text

    assert "event: citations" in text
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line == "event: citations" and i + 1 < len(lines):
            data_line = lines[i + 1]
            assert data_line.startswith("data: ")
            citations = json.loads(data_line[6:])
            assert len(citations) == 1
            assert citations[0]["source_filename"] == "doc.pdf"
            break
    else:
        pytest.fail("citations event not found in SSE stream")


async def test_chat_stream_empty_question(async_client) -> None:
    """POST /chat/stream with an empty question returns 422."""
    response = await async_client.post("/chat/stream", json={"question": ""})
    assert response.status_code == 422


async def test_chat_stream_no_documents(async_client, monkeypatch) -> None:
    """POST /chat/stream completes without error when no documents are stored."""
    import app.rag.pipeline as pipeline_module

    async def fake_generate(prompt: str):
        yield "I couldn't find that in the documents."

    mock_client = MagicMock()
    mock_client.generate = fake_generate

    monkeypatch.setattr(pipeline_module, "retrieve", lambda q: [])
    monkeypatch.setattr(pipeline_module, "get_llm_client", lambda: mock_client)

    response = await async_client.post("/chat/stream", json={"question": "Anything?"})

    assert response.status_code == 200
    assert "event: citations" in response.text
