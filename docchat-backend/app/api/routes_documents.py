"""FastAPI router for document management: upload, list, delete."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.ingestion import IngestionResult, ingest_document
from app.ingestion.parser import DocumentParseError, EmptyDocumentError
from app.retrieval.vector_store import get_vector_store

router = APIRouter()

_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
_READ_CHUNK = (
    1024 * 1024
)  # 1 MB — read in chunks to reject oversized files before buffering all
_ALLOWED_EXTENSIONS = {".pdf", ".docx"}
_MAGIC_BYTES: dict[str, bytes] = {".pdf": b"%PDF-", ".docx": b"PK\x03\x04"}


class _ListResponse(BaseModel):
    documents: list[str]


class _DeleteResponse(BaseModel):
    filename: str
    chunks_deleted: int


@router.post("/upload", response_model=IngestionResult, status_code=200)
async def upload_document(file: UploadFile) -> IngestionResult:
    """Parse, chunk, embed, and store an uploaded document.

    Args:
        file: Multipart file upload. Accepted formats: PDF, DOCX. Max 50 MB.

    Returns:
        Ingestion summary with filename, chunk count, and total character count.

    Raises:
        HTTPException 400: Unsupported file format or magic-byte mismatch.
        HTTPException 413: File exceeds 50 MB.
        HTTPException 422: Document is empty or could not be parsed.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {suffix!r}. Upload a PDF or DOCX file.",
        )

    # Read incrementally so we can reject oversized payloads before buffering the whole file.
    buf = bytearray()
    while chunk := await file.read(_READ_CHUNK):
        buf.extend(chunk)
        if len(buf) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum upload size is 50 MB.",
            )
    content = bytes(buf)

    if not content.startswith(_MAGIC_BYTES[suffix]):
        raise HTTPException(
            status_code=400,
            detail="File content does not match its declared format.",
        )

    try:
        return await run_in_threadpool(ingest_document, content, filename=file.filename)
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
