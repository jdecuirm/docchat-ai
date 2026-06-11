"""Integration tests for the retrieval pipeline (embed → search → rerank).

Marked slow: requires the embedding model (~130 MB) and the reranker model
(~270 MB) to be downloaded on first run. Skip with: pytest -m 'not slow'
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.slow


@pytest.fixture()
def populated_store(tmp_path):
    """A VectorStore pre-loaded with three chunks using real embeddings."""
    from app.ingestion.chunker import Chunk, ChunkMetadata
    from app.ingestion.embedder import embed_texts
    from app.retrieval.vector_store import VectorStore

    store = VectorStore(persist_dir=str(tmp_path))
    texts = [
        "The capital of France is Paris.",
        "Python is a high-level programming language created by Guido van Rossum.",
        "Machine learning uses algorithms to find patterns in large datasets.",
    ]
    chunks = [
        Chunk(
            text=text,
            metadata=ChunkMetadata(
                source_filename="test.pdf",
                page_number=1,
                chunk_index=i + 1,
            ),
        )
        for i, text in enumerate(texts)
    ]
    store.add_chunks(chunks, embed_texts(texts))
    return store


def test_retrieve_returns_ranked_chunks(populated_store, monkeypatch) -> None:
    """retrieve() returns a non-empty list of RankedChunk objects."""
    import app.retrieval as retrieval_module
    from app.retrieval import retrieve
    from app.retrieval.reranker import RankedChunk

    monkeypatch.setattr(retrieval_module, "get_vector_store", lambda: populated_store)

    result = retrieve("What is the capital of France?")

    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(c, RankedChunk) for c in result)


def test_retrieve_respects_top_k_rerank(populated_store, monkeypatch) -> None:
    """retrieve() returns at most top_k_rerank results."""
    import app.retrieval as retrieval_module
    from app.retrieval import retrieve

    monkeypatch.setattr(retrieval_module, "get_vector_store", lambda: populated_store)

    result = retrieve("Python programming", top_k_retrieval=3, top_k_rerank=2)

    assert len(result) <= 2


def test_retrieve_empty_store(tmp_path, monkeypatch) -> None:
    """retrieve() returns [] when the vector store has no documents."""
    import app.retrieval as retrieval_module
    from app.retrieval import retrieve
    from app.retrieval.vector_store import VectorStore

    empty_store = VectorStore(persist_dir=str(tmp_path))
    monkeypatch.setattr(retrieval_module, "get_vector_store", lambda: empty_store)

    result = retrieve("anything")

    assert result == []
