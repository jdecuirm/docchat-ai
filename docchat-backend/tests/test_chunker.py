"""Tests for the document chunker."""

from __future__ import annotations

import pytest

from app.ingestion.chunker import Chunk, ChunkMetadata, chunk_document
from app.ingestion.parser import ParsedDocument, ParsedPage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_doc(pages_text: list[str], filename: str = "test.pdf") -> ParsedDocument:
    """Build a ParsedDocument from a list of per-page strings."""
    pages = [
        ParsedPage(page_number=i + 1, text=text)
        for i, text in enumerate(pages_text)
    ]
    return ParsedDocument(
        filename=filename,
        pages=pages,
        total_chars=sum(len(t) for t in pages_text),
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

def test_chunk_metadata_construction():
    """ChunkMetadata accepts valid 1-indexed fields."""
    meta = ChunkMetadata(source_filename="doc.pdf", page_number=1, chunk_index=1)
    assert meta.source_filename == "doc.pdf"
    assert meta.page_number == 1
    assert meta.chunk_index == 1


def test_chunk_construction():
    """Chunk holds text and metadata."""
    meta = ChunkMetadata(source_filename="doc.pdf", page_number=1, chunk_index=1)
    chunk = Chunk(text="hello world", metadata=meta)
    assert chunk.text == "hello world"
    assert chunk.metadata.chunk_index == 1
