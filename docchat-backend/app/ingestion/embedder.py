"""Embedding wrapper for BAAI/bge-small-en-v1.5 (384-dimensional vectors).

First load downloads ~130 MB from HuggingFace Hub; subsequent loads use
the local cache (~/.cache/huggingface/hub/). The model is loaded once per
process via ``@lru_cache``.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings

__all__ = ["embed_texts", "embed_query"]

# BGE query prefix recommended by the BAAI/bge-small-en-v1.5 model card.
# Applied to queries only — document passages do NOT use a prefix.
_BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load and cache the sentence-transformer model.

    Returns:
        The cached :class:`SentenceTransformer` instance.
    """
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of document passages.

    No query prefix is applied. Use :func:`embed_query` for search queries.

    Args:
        texts: Passage texts to embed.

    Returns:
        A list of 384-dimensional unit-normalized float vectors, one per text.
    """
    model = _get_model()
    vectors = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    """Embed a single search query with the BGE query prefix.

    Args:
        text: The user's search query.

    Returns:
        A 384-dimensional unit-normalized float vector.
    """
    model = _get_model()
    prefixed = _BGE_QUERY_PREFIX + text
    vector = model.encode(
        [prefixed],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    return vector.tolist()
