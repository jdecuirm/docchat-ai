"""Tests for the RAG pipeline: build_prompt and rag_answer."""

from __future__ import annotations

from app.retrieval.reranker import RankedChunk


def _make_chunk(text: str, chunk_index: int = 1, page: int = 1) -> RankedChunk:
    return RankedChunk(
        text=text,
        source_filename="doc.pdf",
        page_number=page,
        chunk_index=chunk_index,
        relevance_score=0.9,
    )


def test_build_prompt_includes_chunk_text() -> None:
    """Each chunk's text appears verbatim in the assembled prompt."""
    from app.rag.pipeline import build_prompt

    chunk = _make_chunk("Paris is the capital of France.")
    prompt = build_prompt("What is the capital?", [chunk])

    assert "Paris is the capital of France." in prompt


def test_build_prompt_numbers_sources() -> None:
    """Chunks are numbered [1], [2], etc. in sequential order."""
    from app.rag.pipeline import build_prompt

    chunks = [_make_chunk("First chunk.", 1), _make_chunk("Second chunk.", 2)]
    prompt = build_prompt("Query?", chunks)

    assert "[1]" in prompt
    assert "[2]" in prompt
    assert prompt.index("[1]") < prompt.index("[2]")


def test_build_prompt_empty_chunks() -> None:
    """When no chunks are available, the no-context message is included."""
    from app.rag.pipeline import build_prompt

    prompt = build_prompt("Query?", [])

    assert "No relevant context" in prompt


def test_build_prompt_includes_query() -> None:
    """The user query appears at the end of the assembled prompt."""
    from app.rag.pipeline import build_prompt

    prompt = build_prompt("What are the main risks?", [])

    assert "What are the main risks?" in prompt


def test_build_prompt_includes_instructions() -> None:
    """The assembled prompt always contains the grounding instructions."""
    from app.rag.pipeline import build_prompt

    prompt = build_prompt("Any question?", [])

    assert "Answer ONLY using the context provided above." in prompt
    assert "I couldn't find that in the documents." in prompt


from unittest.mock import MagicMock


async def test_rag_answer_returns_chunks_and_stream(monkeypatch) -> None:
    """rag_answer returns (list[RankedChunk], async token stream)."""
    import app.rag.pipeline as pipeline_module
    from app.rag.pipeline import rag_answer

    mock_chunks = [_make_chunk("Paris is the capital.")]

    async def fake_generate(prompt: str):
        yield "Hello"
        yield " world"

    mock_client = MagicMock()
    mock_client.generate = fake_generate

    monkeypatch.setattr(pipeline_module, "retrieve", lambda q, where=None: mock_chunks)
    monkeypatch.setattr(pipeline_module, "get_llm_client", lambda: mock_client)

    chunks, stream = await rag_answer("What is Paris?")

    assert chunks == mock_chunks
    tokens = [t async for t in stream]
    assert tokens == ["Hello", " world"]


def test_build_prompt_includes_history() -> None:
    """History turns appear before the context section."""
    from app.rag.pipeline import ConversationTurn, build_prompt

    history = [
        ConversationTurn(role="user", content="What is this document about?"),
        ConversationTurn(role="assistant", content="It is about pipe-sticking."),
    ]
    prompt = build_prompt("Tell me more.", [], history=history)

    assert "[Conversation history]" in prompt
    assert "User: What is this document about?" in prompt
    assert "Assistant: It is about pipe-sticking." in prompt
    # History must appear before context
    assert prompt.index("[Conversation history]") < prompt.index("[Context]")


def test_build_prompt_no_history_section_when_empty() -> None:
    """No history section rendered when history is empty or None."""
    from app.rag.pipeline import build_prompt

    for history in ([], None):
        prompt = build_prompt("Query?", [], history=history)
        assert "[Conversation history]" not in prompt


async def test_rag_answer_passes_history_to_build_prompt(monkeypatch) -> None:
    """rag_answer forwards history to build_prompt; prompt contains history."""
    import app.rag.pipeline as pipeline_module
    from app.rag.pipeline import ConversationTurn, rag_answer

    captured_prompt: list[str] = []

    async def fake_generate(prompt: str):
        captured_prompt.append(prompt)
        yield "answer"

    mock_client = MagicMock()
    mock_client.generate = fake_generate

    history = [ConversationTurn(role="user", content="Prior question")]

    monkeypatch.setattr(pipeline_module, "retrieve", lambda q, where=None: [])
    monkeypatch.setattr(pipeline_module, "get_llm_client", lambda: mock_client)

    _, stream = await rag_answer("Follow-up?", history=history)
    _ = [t async for t in stream]  # consume to trigger generator body

    assert any("Prior question" in p for p in captured_prompt)
