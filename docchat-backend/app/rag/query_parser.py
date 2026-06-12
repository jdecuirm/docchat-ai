"""Extract ChromaDB metadata filters from natural-language queries."""

from __future__ import annotations

import re

__all__ = ["parse_query_filters"]

_PAGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bpages?\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\bp[aá]ginas?\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\bpg\.?\s*(\d+)\b", re.IGNORECASE),
    re.compile(r"\bp\.\s*(\d+)\b", re.IGNORECASE),
]


def parse_query_filters(query: str) -> dict[str, dict[str, int]] | None:
    """Return a ChromaDB where-filter if the query references a page number.

    Supports (case-insensitive): "page 6", "pages 3", "página 6",
    "pagina 6", "p. 12", "pg6", "pg. 6".

    Args:
        query: The user's natural-language question.

    Returns:
        ``{"page_number": {"$eq": N}}`` on first match, or ``None``.
    """
    # Patterns checked in priority order — first match wins.
    for pattern in _PAGE_PATTERNS:
        match = pattern.search(query)
        if match:
            return {"page_number": {"$eq": int(match.group(1))}}
    return None
