"""Tests for query_parser: page-number filter extraction."""

from __future__ import annotations


def test_page_english() -> None:
    """'page N' returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("summarize page 6")
    assert result == {"page_number": {"$eq": 6}}


def test_pages_plural() -> None:
    """'pages N' (plural) returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("what is on pages 3?")
    assert result == {"page_number": {"$eq": 3}}


def test_pagina_spanish() -> None:
    """'página N' (Spanish with accent) returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("resume la página 6 del documento")
    assert result == {"page_number": {"$eq": 6}}


def test_p_dot_notation() -> None:
    """'p. N' notation returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("see p. 12 for details")
    assert result == {"page_number": {"$eq": 12}}


def test_pg_abbreviation() -> None:
    """'pgN' abbreviation (without dot) returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("check pg6 for the table")
    assert result == {"page_number": {"$eq": 6}}


def test_no_page_reference_returns_none() -> None:
    """Queries with no page mention return None."""
    from app.rag.query_parser import parse_query_filters

    assert parse_query_filters("what are the main risks?") is None


def test_empty_string_returns_none() -> None:
    """Empty string returns None."""
    from app.rag.query_parser import parse_query_filters

    assert parse_query_filters("") is None


def test_pg_dot_abbreviation() -> None:
    """'pg. N' abbreviation (with dot) returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("see pg. 8 for the diagram")
    assert result == {"page_number": {"$eq": 8}}


def test_pagina_no_accent() -> None:
    """'pagina N' (no accent) also returns the page filter."""
    from app.rag.query_parser import parse_query_filters

    result = parse_query_filters("ver pagina 3 del manual")
    assert result == {"page_number": {"$eq": 3}}
