"""Tests for the BGE embedder. Marked slow due to ~130 MB model download on first run."""

from __future__ import annotations

import math

import pytest

pytestmark = pytest.mark.slow

EXPECTED_DIM = 384


def _norm(vec: list[float]) -> float:
    """Compute L2 norm of a vector."""
    return math.sqrt(sum(x * x for x in vec))


def test_embed_texts_returns_correct_count():
    """embed_texts returns one vector per input text."""
    from app.ingestion.embedder import embed_texts

    vecs = embed_texts(["hello world", "this is a test"])
    assert len(vecs) == 2


def test_embed_texts_dimension():
    """embed_texts returns 384-dimensional vectors."""
    from app.ingestion.embedder import embed_texts

    vecs = embed_texts(["hello world"])
    assert len(vecs[0]) == EXPECTED_DIM


def test_embed_query_dimension():
    """embed_query returns a single 384-dimensional vector."""
    from app.ingestion.embedder import embed_query

    vec = embed_query("what is machine learning?")
    assert len(vec) == EXPECTED_DIM


def test_embed_texts_normalized():
    """embed_texts produces unit-normalized vectors (norm ≈ 1.0)."""
    from app.ingestion.embedder import embed_texts

    vecs = embed_texts(["normalize me"])
    assert abs(_norm(vecs[0]) - 1.0) < 1e-5


def test_embed_query_normalized():
    """embed_query produces a unit-normalized vector (norm ≈ 1.0)."""
    from app.ingestion.embedder import embed_query

    vec = embed_query("normalize me")
    assert abs(_norm(vec) - 1.0) < 1e-5


def test_embed_texts_vs_embed_query_differ():
    """embed_texts and embed_query differ for the same text (query prefix effect)."""
    from app.ingestion.embedder import embed_query, embed_texts

    text = "machine learning basics"
    passage_vec = embed_texts([text])[0]
    query_vec = embed_query(text)
    assert passage_vec != query_vec


def test_batch_processing():
    """embed_texts handles a batch of N texts and returns N vectors."""
    from app.ingestion.embedder import embed_texts

    texts = [f"document number {i}" for i in range(10)]
    vecs = embed_texts(texts)
    assert len(vecs) == 10
    assert all(len(v) == EXPECTED_DIM for v in vecs)
