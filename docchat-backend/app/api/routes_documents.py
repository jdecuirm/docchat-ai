"""FastAPI router for document management: upload, list, delete."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.ingestion import IngestionResult, ingest_document
from app.ingestion.parser import DocumentParseError, EmptyDocumentError
from app.retrieval.vector_store import get_vector_store

router = APIRouter()

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
_ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class _ListResponse(BaseModel):
    documents: list[str]


class _DeleteResponse(BaseModel):
    filename: str
    chunks_deleted: int


@router.post("/upload", response_model=IngestionResult, status_code=200)
async def upload_document(file: UploadFile) -> IngestionResult:
    """Parse, chunk, embed, and store an uploaded document.

    Args:
        file: Multipart file upload. Accepted formats: PDF, DOCX. Max 10 MB.

    Returns:
        Ingestion summary with filename, chunk count, and total character count.

    Raises:
        HTTPException 400: Unsupported file format.
        HTTPException 413: File exceeds 10 MB.
        HTTPException 422: Document is empty or could not be parsed.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {suffix!r}. Upload a PDF or DOCX file.",
        )

    content = await file.read()
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum upload size is 10 MB.",
        )

    try:
        return ingest_document(content, filename=file.filename)
    except (EmptyDocumentError, DocumentParseError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/", response_model=_ListResponse)
def list_documents() -> _ListResponse:
    """Return the filenames of all ingested documents.

    Returns:
        A sorted list of unique source filenames in the vector store.
    """
    return _ListResponse(documents=get_vector_store().list_documents())


@router.delete("/{filename}", response_model=_DeleteResponse)
def delete_document(filename: str) -> _DeleteResponse:
    """Delete all chunks belonging to a document.

    Args:
        filename: Exact filename used during upload.

    Returns:
        Deletion summary with filename and number of chunks removed.

    Raises:
        HTTPException 404: Document not found in the vector store.
    """
    deleted = get_vector_store().delete_document(filename)
    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Document {filename!r} not found.",
        )
    return _DeleteResponse(filename=filename, chunks_deleted=deleted)
