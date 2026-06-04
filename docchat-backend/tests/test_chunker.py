"""Tests for the document chunker."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

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


# ---------------------------------------------------------------------------
# _build_page_ranges tests
# ---------------------------------------------------------------------------

def test_build_page_ranges_single_page():
    """Single-page doc produces one range starting at 0."""
    from app.ingestion.chunker import _build_page_ranges

    pages = [ParsedPage(page_number=1, text="hello world")]
    ranges = _build_page_ranges(pages, "\n\n")
    assert ranges == [(0, len("hello world"), 1)]


def test_build_page_ranges_multi_page():
    """Multi-page doc ranges account for separator length."""
    from app.ingestion.chunker import _build_page_ranges

    sep = "\n\n"
    p1, p2 = "page one text", "page two text"
    pages = [
        ParsedPage(page_number=1, text=p1),
        ParsedPage(page_number=2, text=p2),
    ]
    ranges = _build_page_ranges(pages, sep)
    assert ranges[0] == (0, len(p1), 1)
    assert ranges[1] == (len(p1) + len(sep), len(p1) + len(sep) + len(p2), 2)


# ---------------------------------------------------------------------------
# _page_for_position tests
# ---------------------------------------------------------------------------

def test_page_for_position_start_of_first_page():
    """Position 0 maps to page 1."""
    from app.ingestion.chunker import _page_for_position

    ranges = [(0, 10, 1), (12, 22, 2)]
    assert _page_for_position(0, ranges) == 1


def test_page_for_position_inside_second_page():
    """Position inside second page range maps to page 2."""
    from app.ingestion.chunker import _page_for_position

    ranges = [(0, 10, 1), (12, 22, 2)]
    assert _page_for_position(15, ranges) == 2


def test_page_for_position_separator_falls_back_to_last_page():
    """Position in separator (between pages) falls back to last page."""
    from app.ingestion.chunker import _page_for_position

    ranges = [(0, 10, 1), (12, 22, 2)]
    assert _page_for_position(10, ranges) == 2  # 10 is in separator (10-11)


# ---------------------------------------------------------------------------
# chunk_document integration tests (slow: loads tokenizer)
# ---------------------------------------------------------------------------

def _make_settings_stub():
    """Return a MagicMock that satisfies the Settings fields used by chunker."""
    stub = MagicMock()
    stub.embedding_model = "BAAI/bge-small-en-v1.5"
    stub.chunk_size = 512
    stub.chunk_overlap = 50
    return stub


@pytest.mark.slow
def test_chunk_document_short_doc():
    """A short single-page doc produces exactly 1 chunk with correct metadata."""
    import app.ingestion.chunker as chunker_mod

    chunker_mod._get_tokenizer.cache_clear()
    doc = make_doc(["This is a short test document with minimal text."])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].metadata.chunk_index == 1
    assert chunks[0].metadata.page_number == 1
    assert chunks[0].metadata.source_filename == "test.pdf"
    assert chunks[0].text.strip()


@pytest.mark.slow
def test_chunk_document_index_starts_at_1():
    """chunk_index starts at 1, not 0."""
    import app.ingestion.chunker as chunker_mod

    chunker_mod._get_tokenizer.cache_clear()
    doc = make_doc(["word " * 400])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert chunks[0].metadata.chunk_index == 1


# ---------------------------------------------------------------------------
# chunk_document behavioral tests (slow: loads tokenizer via @lru_cache)
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_single_page_all_chunks_have_page_1():
    """All chunks from a 1-page doc must have page_number == 1."""
    doc = make_doc(["word " * 400])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert len(chunks) >= 1
    assert all(c.metadata.page_number == 1 for c in chunks)


@pytest.mark.slow
def test_multi_page_first_chunk_on_page_1():
    """First chunk of a multi-page doc must originate on page 1."""
    page1 = "alpha " * 300
    page2 = "beta " * 300
    doc = make_doc([page1, page2])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert chunks[0].metadata.page_number == 1


@pytest.mark.slow
def test_multi_page_last_chunk_on_last_page():
    """Last chunk of a multi-page doc must originate on the last page."""
    page1 = "alpha " * 300
    page2 = "beta " * 300
    doc = make_doc([page1, page2])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert chunks[-1].metadata.page_number == 2


@pytest.mark.slow
def test_chunk_index_sequential_no_gaps():
    """chunk_index is sequential from 1 with no gaps."""
    doc = make_doc(["word " * 600])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    indices = [c.metadata.chunk_index for c in chunks]
    assert indices == list(range(1, len(chunks) + 1))


@pytest.mark.slow
def test_no_empty_chunks():
    """Chunker never returns empty-text chunks."""
    doc = make_doc(["sentence number one. " * 300])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert all(c.text.strip() for c in chunks)


@pytest.mark.slow
def test_source_filename_preserved():
    """source_filename matches the ParsedDocument filename on every chunk."""
    doc = make_doc(["hello world " * 200], filename="report.pdf")
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert all(c.metadata.source_filename == "report.pdf" for c in chunks)


@pytest.mark.slow
def test_short_doc_produces_at_least_one_chunk():
    """A short document produces at least 1 chunk."""
    doc = make_doc(["This is a short document."])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    assert len(chunks) >= 1


@pytest.mark.slow
def test_three_page_doc_page_attribution():
    """Chunks from a 3-page doc span all three page numbers."""
    doc = make_doc(["page one " * 300, "page two " * 300, "page three " * 300])
    with patch("app.ingestion.chunker.get_settings", return_value=_make_settings_stub()):
        chunks = chunk_document(doc)
    page_numbers = {c.metadata.page_number for c in chunks}
    assert 1 in page_numbers
    assert 3 in page_numbers
