"""Clear all ChromaDB vectors so documents can be re-ingested at chunk_size=256.

Run once after updating config defaults:
    uv run python scripts/migrate_rechunk.py

Then re-upload documents through the UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from the project root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.retrieval.vector_store import get_vector_store


def main() -> None:
    """Clear the ChromaDB collection."""
    store = get_vector_store()
    store.clear_collection()
    print("ChromaDB collection cleared.")
    print("Re-upload your documents through the UI to apply the new chunk size.")


if __name__ == "__main__":
    main()
