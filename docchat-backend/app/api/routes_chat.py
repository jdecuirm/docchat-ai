"""FastAPI router for the RAG chat endpoint with SSE streaming."""

from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.rag.pipeline import rag_answer

router = APIRouter()


class _ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


async def _event_stream(query: str) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted strings: token data events, then a citations event.

    On any exception mid-stream, yields an ``event: error`` event instead of
    propagating (HTTP status is already 200 at this point).
    """
    try:
        chunks, stream = await rag_answer(query)
        async for token in stream:
            yield f"data: {token}\n\n"
        citations = [chunk.model_dump() for chunk in chunks]
        yield f"event: citations\ndata: {json.dumps(citations)}\n\n"
    except Exception as exc:
        yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"


@router.post("/stream")
async def chat_stream(request: _ChatRequest) -> StreamingResponse:
    """Stream an LLM answer using the RAG pipeline over Server-Sent Events.

    Emits SSE over a persistent HTTP connection:

    - ``data: <token>`` — one event per LLM output token
    - ``event: citations`` — JSON array of source chunks after the last token
    - ``event: error`` — error description if generation fails mid-stream

    The frontend must use ``fetch`` + ``ReadableStream`` (not the browser-native
    ``EventSource`` API, which does not support POST).

    Args:
        request: JSON body with a ``question`` field (1–2000 characters).

    Returns:
        A ``text/event-stream`` streaming response.
    """
    return StreamingResponse(
        _event_stream(request.question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
