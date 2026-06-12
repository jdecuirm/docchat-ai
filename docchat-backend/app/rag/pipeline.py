"""RAG orchestration pipeline: retrieve context, build prompt, stream answer."""

from __future__ import annotations


from app.retrieval.reranker import RankedChunk

__all__ = ["build_prompt"]


def build_prompt(query: str, chunks: list[RankedChunk]) -> str:
    """Assemble a RAG prompt from re-ranked context chunks and a user query.

    Each chunk is formatted as ``[N] filename  p.X — <text>``. Fixed
    instructions tell the LLM to answer only from context and cite with
    ``[N]`` notation. When no chunks are available, a no-context message
    replaces the context section.

    Args:
        query: The user's natural-language question.
        chunks: Re-ranked context chunks from the retrieval pipeline.

    Returns:
        A fully assembled prompt string ready for the LLM.
    """
    if chunks:
        context_section = "\n\n".join(
            f"[{i + 1}] {chunk.source_filename} p.{chunk.page_number} — {chunk.text}"
            for i, chunk in enumerate(chunks)
        )
    else:
        context_section = "No relevant context was found in the uploaded documents."

    return (
        f"{context_section}\n\n"
        "Answer ONLY using the context provided above.\n"
        "Cite sources inline using [N] notation.\n"
        "If the context does not contain enough information to answer the question, "
        'respond with: "I couldn\'t find that in the documents."\n'
        "Do not speculate or add information beyond what is in the context.\n\n"
        f"Question: {query}"
    )
