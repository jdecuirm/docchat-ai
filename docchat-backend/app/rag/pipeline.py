"""RAG orchestration pipeline: retrieve context, build prompt, stream answer."""

from __future__ import annotations

from typing import AsyncGenerator, Literal

from pydantic import BaseModel

from app.llm import get_llm_client
from app.retrieval import retrieve
from app.retrieval.reranker import RankedChunk

__all__ = ["ConversationTurn", "build_prompt", "rag_answer"]


class ConversationTurn(BaseModel):
    """A single turn in the conversation history sent by the client.

    Attributes:
        role: Speaker — ``"user"`` or ``"assistant"``.
        content: The full message text for this turn.
    """

    role: Literal["user", "assistant"]
    content: str


def build_prompt(
    query: str,
    chunks: list[RankedChunk],
    history: list[ConversationTurn] | None = None,
) -> str:
    """Assemble a RAG prompt from conversation history, context chunks, and query.

    Prompt structure (history section omitted when empty):

        [Conversation history]
        User: ...
        Assistant: ...

        [Context]
        [1] filename p.N — text
        ...

        Answer ONLY using the context provided above. ...

        Question: <query>

    Args:
        query: The user's natural-language question.
        chunks: Re-ranked context chunks from the retrieval pipeline.
        history: Previous conversation turns, oldest first. Defaults to None.

    Returns:
        A fully assembled prompt string ready for the LLM.
    """
    parts: list[str] = []

    if history:
        history_lines = "\n".join(
            f"{'User' if turn.role == 'user' else 'Assistant'}: {turn.content}"
            for turn in history
        )
        parts.append(f"[Conversation history]\n{history_lines}")

    if chunks:
        context_body = "\n\n".join(
            f"[{i + 1}] {chunk.source_filename} p.{chunk.page_number} — {chunk.text}"
            for i, chunk in enumerate(chunks)
        )
    else:
        context_body = "No relevant context was found in the uploaded documents."

    parts.append(f"[Context]\n{context_body}")

    parts.append(
        "Answer ONLY using the context provided above.\n"
        "Cite sources inline using [N] notation.\n"
        "If the context does not contain enough information to answer the question, "
        'respond with: "I couldn\'t find that in the documents."\n'
        "Do not speculate or add information beyond what is in the context.\n\n"
        f"Question: {query}"
    )

    return "\n\n".join(parts)


async def rag_answer(
    query: str,
    history: list[ConversationTurn] | None = None,
) -> tuple[list[RankedChunk], AsyncGenerator[str, None]]:
    """Retrieve relevant context and prepare a streaming LLM answer.

    Args:
        query: The user's natural-language question.
        history: Previous conversation turns for context. Defaults to None.

    Returns:
        ``(chunks, token_stream)`` where ``chunks`` are the re-ranked context
        chunks (used for citations) and ``token_stream`` yields LLM tokens.
    """
    chunks = retrieve(query)
    prompt = build_prompt(query, chunks, history=history)
    stream = get_llm_client().generate(prompt)
    return chunks, stream
