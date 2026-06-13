"""BGE cross-encoder re-ranker for retrieved document chunks.

First load downloads ~270 MB from HuggingFace Hub; subsequent loads use
the local cache (~/.cache/huggingface/hub/). The model is loaded once per
process via ``@lru_cache``.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel

from app.config import get_settings
from app.retrieval.vector_store import RetrievedChunk

__all__ = ["RankedChunk", "rerank"]


class RankedChunk(BaseModel):
    """A chunk scored and re-ranked by the BGE cross-encoder.

    Attributes:
        text: The chunk's text content.
        source_filename: Name of the source document.
        page_number: 1-indexed page within the source document.
        chunk_index: 1-indexed position within the document.
        relevance_score: Cross-encoder relevance score (higher = more relevant).
            Distinct from ChromaDB's cosine distance: this score reflects
            semantic relevance to the query, not vector similarity.
    """

    text: str
    source_filename: str
    page_number: int
    chunk_index: int
    relevance_score: float


@lru_cache(maxsize=1)
def _get_reranker():
    """Load and cache the BGE cross-encoder model."""
    from sentence_transformers import CrossEncoder

    settings = get_settings()
    return CrossEncoder(settings.reranker_model)


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    top_k: int,
) -> list[RankedChunk]:
    """Score and re-rank candidate chunks using the BGE cross-encoder.

    Args:
        query: The user's search query.
        chunks: Candidate chunks from the vector store (unordered).
        top_k: Maximum number of results to return.

    Returns:
        Up to ``top_k`` :class:`RankedChunk` objects ordered by descending
        relevance score. Returns an empty list when ``chunks`` is empty.
    """
    if not chunks:
        return []

    pairs = [(query, chunk.text) for chunk in chunks]
    scores = _get_reranker().predict(pairs)

    scored = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

    return [
        RankedChunk(
            text=chunk.text,
            source_filename=chunk.source_filename,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            relevance_score=float(score),
        )
        for chunk, score in scored[:top_k]
    ]
