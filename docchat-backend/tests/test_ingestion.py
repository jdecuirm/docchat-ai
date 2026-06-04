"""Integration test for the ingest_document() orchestrator.

Marked slow because embed_texts() loads the BGE model (~130 MB on first run).
"""

from __future__ import annotations

import pytest

from app.ingestion import IngestionResult, ingest_document
from app.retrieval.vector_store import VectorStore

pytestmark = pytest.mark.slow


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    """Replace the process-level vector store with a tmp_path-backed one."""
    store = VectorStore(persist_dir=str(tmp_path))
    monkeypatch.setattr("app.ingestion.get_vector_store", lambda: store)
    return store


def test_ingest_document_returns_result(isolated_store):
    """ingest_document returns an IngestionResult with correct shape."""
    content = "This is a test document. " * 50
    result = ingest_document(content.encode(), filename="test.txt")

    assert isinstance(result, IngestionResult)
    assert result.filename == "test.txt"
    assert result.num_chunks >= 1
    assert result.total_chars > 0


def test_ingest_document_stores_chunks(isolated_store):
    """After ingestion, list_documents contains the filename."""
    content = "Sample content for ingestion. " * 50
    ingest_document(content.encode(), filename="sample.txt")

    assert "sample.txt" in isolated_store.list_documents()


def test_ingest_document_idempotent(isolated_store):
    """Re-ingesting the same document does not duplicate chunks."""
    content = "Idempotence test. " * 50
    ingest_document(content.encode(), filename="idem.txt")
    result1 = ingest_document(content.encode(), filename="idem.txt")
    result2 = ingest_document(content.encode(), filename="idem.txt")

    assert result1.num_chunks == result2.num_chunks
    assert isolated_store.list_documents().count("idem.txt") == 1
