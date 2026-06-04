"""Tests for the ChromaDB vector store. Uses tmp_path to avoid polluting ./chroma_data."""

from __future__ import annotations

import pytest

from app.ingestion.chunker import Chunk, ChunkMetadata
from app.retrieval.vector_store import VectorStore

EMBEDDING_DIM = 384


def make_chunk(
    filename: str,
    chunk_index: int,
    page: int = 1,
    text: str = "",
) -> Chunk:
    """Build a synthetic Chunk for testing."""
    return Chunk(
        text=text or f"chunk text {chunk_index}",
        metadata=ChunkMetadata(
            source_filename=filename,
            page_number=page,
            chunk_index=chunk_index,
        ),
    )


def make_embedding(dim: int = EMBEDDING_DIM, seed: float = 0.1) -> list[float]:
    """Build a unit-normalized synthetic embedding."""
    vec = [seed] * dim
    norm = sum(x * x for x in vec) ** 0.5
    return [x / norm for x in vec]


@pytest.fixture()
def store(tmp_path) -> VectorStore:
    """Isolated VectorStore backed by a temporary directory."""
    return VectorStore(persist_dir=str(tmp_path))


def test_add_and_list_documents(store: VectorStore) -> None:
    """Adding chunks makes the document appear in list_documents."""
    chunks = [make_chunk("report.pdf", 1), make_chunk("report.pdf", 2)]
    embeddings = [make_embedding(), make_embedding(seed=0.2)]
    store.add_chunks(chunks, embeddings)
    assert "report.pdf" in store.list_documents()


def test_list_documents_empty(store: VectorStore) -> None:
    """Empty store returns an empty list."""
    assert store.list_documents() == []


def test_delete_document_removes_chunks(store: VectorStore) -> None:
    """delete_document removes all chunks and the filename disappears."""
    chunks = [make_chunk("doc.pdf", 1), make_chunk("doc.pdf", 2)]
    embeddings = [make_embedding(), make_embedding(seed=0.2)]
    store.add_chunks(chunks, embeddings)

    deleted = store.delete_document("doc.pdf")

    assert deleted == 2
    assert "doc.pdf" not in store.list_documents()


def test_delete_nonexistent_document_returns_zero(store: VectorStore) -> None:
    """Deleting a non-existent document returns 0."""
    assert store.delete_document("ghost.pdf") == 0


def test_idempotent_ingestion_no_duplicates(store: VectorStore) -> None:
    """Re-ingesting the same document does not duplicate chunks."""
    chunks = [make_chunk("report.pdf", 1), make_chunk("report.pdf", 2)]
    embeddings = [make_embedding(), make_embedding(seed=0.2)]

    store.add_chunks(chunks, embeddings)
    store.add_chunks(chunks, embeddings)  # second ingestion

    result = store._collection.get(
        where={"source_filename": "report.pdf"},
        include=[],
    )
    assert len(result["ids"]) == 2  # still 2, not 4


def test_query_returns_retrieved_chunks(store: VectorStore) -> None:
    """query returns RetrievedChunk objects with all fields populated."""
    chunks = [make_chunk("doc.pdf", 1, text="the quick brown fox")]
    embeddings = [make_embedding()]
    store.add_chunks(chunks, embeddings)

    results = store.query(embedding=make_embedding(), top_k=5)

    assert len(results) == 1
    assert results[0].source_filename == "doc.pdf"
    assert results[0].chunk_index == 1
    assert results[0].page_number == 1
    assert isinstance(results[0].distance, float)


def test_query_empty_store_returns_empty_list(store: VectorStore) -> None:
    """query on an empty store returns an empty list."""
    results = store.query(embedding=make_embedding(), top_k=5)
    assert results == []


def test_multiple_documents_listed(store: VectorStore) -> None:
    """list_documents returns all unique filenames."""
    store.add_chunks([make_chunk("a.pdf", 1)], [make_embedding()])
    store.add_chunks([make_chunk("b.pdf", 1)], [make_embedding(seed=0.2)])

    docs = store.list_documents()
    assert "a.pdf" in docs
    assert "b.pdf" in docs
