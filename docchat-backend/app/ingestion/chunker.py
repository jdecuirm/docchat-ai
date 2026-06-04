"""Chunking: split ParsedDocument into overlapping text chunks with citation metadata."""

from __future__ import annotations

from functools import lru_cache

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from transformers import AutoTokenizer

from app.config import get_settings
from app.ingestion.parser import ParsedDocument, ParsedPage

__all__ = ["ChunkMetadata", "Chunk", "chunk_document"]

_PAGE_SEPARATOR = "\n\n"


class ChunkMetadata(BaseModel):
    """Citation metadata attached to every chunk.

    Attributes:
        source_filename: Base name of the source document.
        page_number: 1-indexed page containing the chunk's first character.
        chunk_index: 1-indexed sequential position within the document.
    """

    source_filename: str
    page_number: int = Field(ge=1)
    chunk_index: int = Field(ge=1)


class Chunk(BaseModel):
    """A text chunk with its citation metadata.

    Attributes:
        text: The chunk text as extracted from the source document.
        metadata: Citation fields used to build source references.
    """

    text: str
    metadata: ChunkMetadata


@lru_cache(maxsize=1)
def _get_tokenizer() -> AutoTokenizer:
    """Load and cache the embedding model tokenizer.

    Returns:
        The cached AutoTokenizer instance for the configured embedding model.
    """
    settings = get_settings()
    return AutoTokenizer.from_pretrained(settings.embedding_model)


def _build_page_ranges(
    pages: list[ParsedPage],
    separator: str,
) -> list[tuple[int, int, int]]:
    """Map each page to its character range in the concatenated text.

    Args:
        pages: Pages in document order.
        separator: String inserted between pages during concatenation.

    Returns:
        List of (start_char, end_char_exclusive, page_number) tuples.
    """
    ranges: list[tuple[int, int, int]] = []
    offset = 0
    for i, page in enumerate(pages):
        start = offset
        end = offset + len(page.text)
        ranges.append((start, end, page.page_number))
        if i < len(pages) - 1:
            offset = end + len(separator)
    return ranges


def _page_for_position(
    pos: int,
    page_ranges: list[tuple[int, int, int]],
) -> int:
    """Find the page number that contains character position *pos*.

    Args:
        pos: Character index in the concatenated text.
        page_ranges: Output of :func:`_build_page_ranges`.

    Returns:
        The 1-indexed page number, or the last page for separator positions.
    """
    for start, end, page_num in page_ranges:
        if start <= pos < end:
            return page_num
    return page_ranges[-1][2]


def chunk_document(parsed: ParsedDocument) -> list[Chunk]:
    """Split a ParsedDocument into overlapping chunks with citation metadata.

    Concatenates all pages with a double-newline separator to preserve cross-
    page text flow, then splits using the embedding model's tokenizer so that
    CHUNK_SIZE is measured in tokens (not characters).

    Page attribution: each chunk is assigned the page that contains its first
    character in the concatenated text.

    Args:
        parsed: A ParsedDocument produced by Stage B.

    Returns:
        Chunks in document order with 1-indexed chunk_index.
    """
    settings = get_settings()

    full_text = _PAGE_SEPARATOR.join(page.text for page in parsed.pages)
    page_ranges = _build_page_ranges(parsed.pages, _PAGE_SEPARATOR)

    tokenizer = _get_tokenizer()
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer=tokenizer,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    chunk_texts = splitter.split_text(full_text)

    chunks: list[Chunk] = []
    search_offset = 0

    for idx, text in enumerate(chunk_texts, start=1):
        pos = full_text.find(text, search_offset)
        if pos == -1:
            pos = full_text.find(text)
        if pos == -1:
            raise RuntimeError(
                f"Chunk text not found in full_text after retry: {text[:50]!r}"
            )
        page_num = _page_for_position(pos, page_ranges)
        search_offset = pos + 1

        chunks.append(
            Chunk(
                text=text,
                metadata=ChunkMetadata(
                    source_filename=parsed.filename,
                    page_number=page_num,
                    chunk_index=idx,
                ),
            )
        )

    return chunks
