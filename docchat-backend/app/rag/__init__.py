"""RAG orchestration layer — retrieve context, build prompt, stream answer."""

from __future__ import annotations

from app.rag.pipeline import rag_answer

__all__ = ["rag_answer"]
