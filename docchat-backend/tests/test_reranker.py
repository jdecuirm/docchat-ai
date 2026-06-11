"""Tests for the BGE cross-encoder re-ranker."""

from __future__ import annotations

import pytest


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
