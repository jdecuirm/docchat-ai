"""Retrieval pipeline: embed query → vector search → cross-encoder re-rank."""

from __future__ import annotations

from app.config import get_settings
from app.ingestion.embedder import embed_query
from app.retrieval.reranker import RankedChunk, rerank
from app.retrieval.vector_store import get_vector_store

__all__ = ["retrieve"]


def retrieve(
    query: str,
    top_k_retrieval: int | None = None,
    top_k_rerank: int | None = None,
) -> list[RankedChunk]:
    """Embed a query, find candidate chunks, and re-rank them.

    Args:
        query: The user's natural-language search query.
        top_k_retrieval: Candidates to pull from ChromaDB. Defaults to
            ``settings.top_k_retrieval`` (10).
        top_k_rerank: Results to keep after re-ranking. Defaults to
            ``settings.top_k_rerank`` (4).

    Returns:
        Up to ``top_k_rerank`` :class:`RankedChunk` objects ordered by
        descending relevance score, or an empty list if the store is empty.
    """
    settings = get_settings()
    k_retrieval = (
        top_k_retrieval if top_k_retrieval is not None else settings.top_k_retrieval
    )
    k_rerank = top_k_rerank if top_k_rerank is not None else settings.top_k_rerank

    embedding = embed_query(query)
    candidates = get_vector_store().query(embedding, top_k=k_retrieval)
    return rerank(query, candidates, top_k=k_rerank)
