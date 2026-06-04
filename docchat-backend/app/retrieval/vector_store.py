"""ChromaDB vector store for embedded document chunks.

Uses a single persistent collection ``"documents"`` with cosine distance.
The public singleton ``get_vector_store()`` follows the same ``@lru_cache``
pattern as ``get_settings()``.
"""

from __future__ import annotations

from functools import lru_cache

import chromadb
from pydantic import BaseModel

from app.config import get_settings
from app.ingestion.chunker import Chunk

__all__ = ["RetrievedChunk", "VectorStore", "get_vector_store"]

_COLLECTION_NAME = "documents"


class RetrievedChunk(BaseModel):
    """A chunk returned by a similarity search.

    Attributes:
        text: The chunk's text content.
        source_filename: Name of the source document.
        page_number: 1-indexed page within the source document.
        chunk_index: 1-indexed position within the document.
        distance: Cosine distance from the query vector (lower = more similar).
    """

    text: str
    source_filename: str
    page_number: int
    chunk_index: int
    distance: float


class VectorStore:
    """Wrapper around a ChromaDB persistent collection for document chunks."""

    def __init__(self, persist_dir: str) -> None:
        """Initialize the client and ensure the collection exists.

        Args:
            persist_dir: Directory path where ChromaDB persists data on disk.
        """
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """Store chunks and embeddings, replacing any prior version of the document.

        Idempotent: existing chunks for the same source_filename are deleted
        before inserting the new batch. This prevents stale chunks when a
        document is re-ingested after a settings change.

        Args:
            chunks: Chunks to store; all must share the same source_filename.
            embeddings: Embedding vector per chunk (same order and length).
        """
        if not chunks:
            return

        if len(embeddings) != len(chunks):
            raise ValueError(
                f"Expected {len(chunks)} embeddings, got {len(embeddings)}."
            )

        filename = chunks[0].metadata.source_filename
        self.delete_document(filename)

        ids = [
            f"{c.metadata.source_filename}::{c.metadata.chunk_index}"
            for c in chunks
        ]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "source_filename": c.metadata.source_filename,
                "page_number": c.metadata.page_number,
                "chunk_index": c.metadata.chunk_index,
            }
            for c in chunks
        ]

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def list_documents(self) -> list[str]:
        """Return unique filenames of all ingested documents.

        Note: fetches all metadatas into memory. Acceptable at portfolio scale.
        For 100K+ chunks a sidecar metadata table would be more efficient.

        Returns:
            Sorted list of unique source_filename values.
        """
        result = self._collection.get(include=["metadatas"])
        seen: set[str] = set()
        for meta in result["metadatas"]:
            if meta and "source_filename" in meta:
                seen.add(str(meta["source_filename"]))
        return sorted(seen)

    def delete_document(self, filename: str) -> int:
        """Delete all chunks belonging to a document.

        Args:
            filename: The source_filename value used during ingestion.

        Returns:
            Number of chunks deleted (0 if the document was not found).
        """
        result = self._collection.get(
            where={"source_filename": filename},
            include=[],
        )
        ids = result["ids"]
        if ids:
            self._collection.delete(ids=ids)
        return len(ids)

    def query(
        self,
        embedding: list[float],
        top_k: int,
    ) -> list[RetrievedChunk]:
        """Find the most similar chunks for a query embedding.

        Args:
            embedding: Query vector (must match collection dimensionality).
            top_k: Maximum number of results to return.

        Returns:
            List of :class:`RetrievedChunk` ordered by ascending distance.
        """
        n_results = min(top_k, self._collection.count())
        if n_results == 0:
            return []

        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        retrieved: list[RetrievedChunk] = []
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            retrieved.append(
                RetrievedChunk(
                    text=doc,
                    source_filename=str(meta["source_filename"]),
                    page_number=int(meta["page_number"]),
                    chunk_index=int(meta["chunk_index"]),
                    distance=float(dist),
                )
            )
        return retrieved


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """Return the cached VectorStore instance for the process.

    Returns:
        The singleton :class:`VectorStore` backed by ``settings.chroma_persist_dir``.
    """
    settings = get_settings()
    return VectorStore(persist_dir=settings.chroma_persist_dir)
