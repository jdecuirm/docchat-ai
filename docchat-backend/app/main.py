"""FastAPI application entry point for the DocChat AI backend.

Run locally with::

    uv run uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_documents import router as documents_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="DocChat AI",
    description=(
        "RAG chatbot for documents. Upload PDFs/DOCX and ask grounded "
        "questions with source citations."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Liveness probe for deploy platforms and the frontend.

    Returns:
        A mapping with a single ``status`` key set to ``"ok"``.
    """
    return {"status": "ok"}


app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
