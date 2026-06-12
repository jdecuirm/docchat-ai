"""Tests for the document management API endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_upload_pdf_success(client: TestClient, monkeypatch) -> None:
    """POST /documents/upload with a PDF returns 200 and ingestion summary."""
    import app.api.routes_documents as routes_module
    from app.ingestion import IngestionResult

    monkeypatch.setattr(
        routes_module,
        "ingest_document",
        lambda content, filename: IngestionResult(
            filename=filename, num_chunks=10, total_chars=500
        ),
    )

    response = client.post(
        "/documents/upload",
        files={"file": ("report.pdf", b"fake pdf content", "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "report.pdf"
    assert data["num_chunks"] == 10


def test_upload_unsupported_format(client: TestClient) -> None:
    """POST /documents/upload with .txt returns 400."""
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"some text", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_empty_document(client: TestClient, monkeypatch) -> None:
    """POST /documents/upload returns 422 when document has no extractable text."""
    import app.api.routes_documents as routes_module
    from app.ingestion.parser import EmptyDocumentError

    def raise_empty(content, filename):
        raise EmptyDocumentError("no text found")

    monkeypatch.setattr(routes_module, "ingest_document", raise_empty)

    response = client.post(
        "/documents/upload",
        files={"file": ("empty.pdf", b"fake pdf", "application/pdf")},
    )
    assert response.status_code == 422


def test_upload_file_too_large(client: TestClient) -> None:
    """POST /documents/upload with a file > 10 MB returns 413."""
    oversized_content = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/documents/upload",
        files={"file": ("big.pdf", oversized_content, "application/pdf")},
    )
    assert response.status_code == 413


def test_list_documents_empty(client: TestClient, monkeypatch) -> None:
    """GET /documents/ returns empty list when no documents are stored."""
    import app.api.routes_documents as routes_module

    mock_store = MagicMock()
    mock_store.list_documents.return_value = []
    monkeypatch.setattr(routes_module, "get_vector_store", lambda: mock_store)

    response = client.get("/documents/")

    assert response.status_code == 200
    assert response.json() == {"documents": []}


def test_list_documents_after_upload(client: TestClient, monkeypatch) -> None:
    """GET /documents/ returns filenames of all stored documents."""
    import app.api.routes_documents as routes_module

    mock_store = MagicMock()
    mock_store.list_documents.return_value = ["report.pdf", "notes.docx"]
    monkeypatch.setattr(routes_module, "get_vector_store", lambda: mock_store)

    response = client.get("/documents/")

    assert response.status_code == 200
    assert response.json() == {"documents": ["report.pdf", "notes.docx"]}


def test_delete_existing_document(client: TestClient, monkeypatch) -> None:
    """DELETE /documents/{filename} returns 200 with chunks_deleted count."""
    import app.api.routes_documents as routes_module

    mock_store = MagicMock()
    mock_store.delete_document.return_value = 12
    monkeypatch.setattr(routes_module, "get_vector_store", lambda: mock_store)

    response = client.delete("/documents/report.pdf")

    assert response.status_code == 200
    assert response.json() == {"filename": "report.pdf", "chunks_deleted": 12}


def test_delete_nonexistent_document(client: TestClient, monkeypatch) -> None:
    """DELETE /documents/{filename} returns 404 when document is not found."""
    import app.api.routes_documents as routes_module

    mock_store = MagicMock()
    mock_store.delete_document.return_value = 0
    monkeypatch.setattr(routes_module, "get_vector_store", lambda: mock_store)

    response = client.delete("/documents/nonexistent.pdf")

    assert response.status_code == 404
