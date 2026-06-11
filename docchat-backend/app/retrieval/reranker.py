"""BGE cross-encoder re-ranker for retrieved document chunks.

First load downloads ~270 MB from HuggingFace Hub; subsequent loads use
the local cache (~/.cache/huggingface/hub/). The model is loaded once per
process via ``@lru_cache``.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel
from sentence_transformers import CrossEncoder

from app.config import get_settings

__all__ = ["RankedChunk"]


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
def _get_reranker() -> CrossEncoder:
    """Load and cache the BGE cross-encoder model.

    Returns:
        The cached :class:`CrossEncoder` instance.
    """
    settings = get_settings()
    return CrossEncoder(settings.reranker_model)
