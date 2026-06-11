"""Tests for the BGE cross-encoder re-ranker."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock


def test_ranked_chunk_fields() -> None:
    """RankedChunk stores all citation fields and a float relevance_score."""
    from app.retrieval.reranker import RankedChunk

    chunk = RankedChunk(
        text="some passage text",
        source_filename="doc.pdf",
        page_number=2,
        chunk_index=5,
        relevance_score=0.87,
    )

    assert chunk.text == "some passage text"
    assert chunk.source_filename == "doc.pdf"
    assert chunk.page_number == 2
    assert chunk.chunk_index == 5
    assert chunk.relevance_score == pytest.approx(0.87)


def _make_retrieved(text: str, chunk_index: int) -> "RetrievedChunk":
    from app.retrieval.vector_store import RetrievedChunk

    return RetrievedChunk(
        text=text,
        source_filename="doc.pdf",
        page_number=1,
        chunk_index=chunk_index,
        distance=0.1,
    )


@pytest.fixture()
def mock_reranker(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch _get_reranker so no model is downloaded in unit tests."""
    mock = MagicMock()
    monkeypatch.setattr("app.retrieval.reranker._get_reranker", lambda: mock)
    return mock


def test_rerank_orders_by_score(mock_reranker: MagicMock) -> None:
    """rerank() returns chunks sorted by descending relevance_score."""
    from app.retrieval.reranker import rerank

    chunks = [_make_retrieved("low relevance", 1), _make_retrieved("high relevance", 2)]
    mock_reranker.predict.return_value = [0.1, 0.9]

    result = rerank("some query", chunks, top_k=2)

    assert result[0].chunk_index == 2  # high relevance first
    assert result[1].chunk_index == 1
    assert result[0].relevance_score > result[1].relevance_score


def test_rerank_cuts_to_top_k(mock_reranker: MagicMock) -> None:
    """rerank() returns at most top_k chunks."""
    from app.retrieval.reranker import rerank

    chunks = [_make_retrieved(f"chunk {i}", i) for i in range(5)]
    mock_reranker.predict.return_value = [0.1, 0.5, 0.9, 0.3, 0.7]

    result = rerank("some query", chunks, top_k=3)

    assert len(result) == 3


def test_rerank_empty_input(mock_reranker: MagicMock) -> None:
    """rerank() returns [] without calling the model when chunks is empty."""
    from app.retrieval.reranker import rerank

    result = rerank("some query", [], top_k=4)

    assert result == []
    mock_reranker.predict.assert_not_called()


def test_rerank_fewer_than_top_k(mock_reranker: MagicMock) -> None:
    """rerank() returns all chunks when len(chunks) < top_k (no error)."""
    from app.retrieval.reranker import rerank

    chunks = [_make_retrieved("only chunk", 1)]
    mock_reranker.predict.return_value = [0.8]

    result = rerank("some query", chunks, top_k=4)

    assert len(result) == 1
    assert result[0].relevance_score == pytest.approx(0.8)
