"""Document ingestion pipeline: parse → chunk → embed → store.

Public API:
    ingest_document(source, filename) -> IngestionResult
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from app.ingestion.chunker import chunk_document
from app.ingestion.embedder import embed_texts
from app.ingestion.parser import parse_document
from app.retrieval.vector_store import get_vector_store

__all__ = ["IngestionResult", "ingest_document"]


class IngestionResult(BaseModel):
    """Summary of a completed ingestion run.

    Attributes:
        filename: Base name of the ingested document.
        num_chunks: Number of chunks stored in the vector store.
        total_chars: Total character count of extracted text.
    """

    filename: str
    num_chunks: int
    total_chars: int


def ingest_document(
    source: str | Path | bytes,
    filename: str | None = None,
) -> IngestionResult:
    """Parse, chunk, embed, and store a document end-to-end.

    This is the high-level API consumed by FastAPI endpoints (Stage F). It
    orchestrates Stage B (parsing) and Stage C (chunking, embedding, storage).

    Args:
        source: Filesystem path or raw file bytes.
        filename: Required when ``source`` is bytes; optional override otherwise.

    Returns:
        An :class:`IngestionResult` summarising what was ingested.

    Raises:
        DocumentParseError: If the file is corrupt or the format is unsupported.
        EmptyDocumentError: If no text can be extracted from the file.
    """
    parsed = parse_document(source, filename=filename)
    chunks = chunk_document(parsed)
    embeddings = embed_texts([c.text for c in chunks])
    get_vector_store().add_chunks(chunks, embeddings)
    return IngestionResult(
        filename=parsed.filename,
        num_chunks=len(chunks),
        total_chars=parsed.total_chars,
    )
