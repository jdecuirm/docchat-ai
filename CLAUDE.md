# DocChat AI — Project Context for Claude Code

## What this is
A RAG (Retrieval-Augmented Generation) chatbot for documents. Users upload
PDFs/DOCX files and ask questions; the system retrieves relevant chunks and
generates grounded answers with source citations. Built as a portfolio piece
to showcase AI engineering skills.

## Owner
Jorge Decuir (github.com/jdecuirm). Solo developer.

## Core principles
- Build incrementally by stages (A through I). STOP at each checkpoint and
  wait for explicit green light before advancing.
- NO commits or pushes without explicit approval.
- Clean, production-quality code. This is a portfolio piece — it must impress.
- English for all code, comments, docs, and UI strings.
- Type hints on all Python functions. Docstrings on public functions/classes.

## Tech stack (do not deviate without asking)
- Package manager: uv (NOT pip/poetry directly)
- Backend: FastAPI + uvicorn + pydantic + pydantic-settings
- Document parsing: pypdf, python-docx
- Chunking: langchain-text-splitters (RecursiveCharacterTextSplitter)
- Embeddings: sentence-transformers, model BAAI/bge-small-en-v1.5 (local, 384-dim)
- Vector DB: ChromaDB (embedded, persistent on disk)
- Re-ranking: BAAI/bge-reranker-base (sentence-transformers CrossEncoder)
- LLM: provider-switchable via env var LLM_PROVIDER
    - "ollama" for development (model: llama3.2, via http://localhost:11434)
    - "claude" for demo/production (Anthropic API, model claude-haiku-4-5)
- Frontend: React + Vite + Tailwind (chat UI with streaming + source citations)
- Deploy: Render (backend web service + static frontend)
- Tests: pytest
- Linting: ruff

## LLM abstraction (critical design)
Implement a common interface in app/llm/base.py so the rest of the code never
imports Ollama or Anthropic directly. Switching providers = changing one env
var. Both clients implement the same generate(prompt, context_chunks) method
and support streaming.

## Project structure
docchat-ai/
├── docchat-backend/
│   └── app/
│       ├── main.py              # FastAPI app
│       ├── config.py            # pydantic-settings from .env
│       ├── ingestion/           # parser.py, chunker.py, embedder.py
│       ├── retrieval/           # vector_store.py, reranker.py
│       ├── llm/                 # base.py, ollama_client.py, claude_client.py
│       ├── rag/                 # pipeline.py (orchestrates retrieval + LLM)
│       └── api/                 # routes_documents.py, routes_chat.py
└── docchat-frontend/            # React + Vite

## RAG pipeline design
1. Ingestion: file → parse → clean text → chunk (512 tokens, 50 overlap)
   → embed → store in ChromaDB with metadata (filename, page, chunk_index)
2. Query: question → embed → retrieve TOP_K_RETRIEVAL=10 from ChromaDB
   → re-rank with BGE reranker → keep TOP_K_RERANK=4
   → build prompt with chunks → LLM generates → return answer + citations
3. The LLM prompt MUST instruct: answer ONLY from provided context, cite
   sources, and say "I couldn't find that in the documents" when context
   is insufficient. NO hallucinations.

## Config defaults (app/config.py via pydantic-settings)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
ANTHROPIC_API_KEY=(optional)
CLAUDE_MODEL=claude-haiku-4-5
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
RERANKER_MODEL=BAAI/bge-reranker-base
CHROMA_PERSIST_DIR=./chroma_data
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=10
TOP_K_RERANK=4

## Security / privacy (portfolio talking points)
- API keys ONLY in .env, never committed. .env.example has placeholders.
- All secrets via environment variables.
- When using Claude API: data is never used for training (commercial terms),
  7-day retention. Document this in the README as a privacy feature.

## Build stages & checkpoints
- Stage A: Scaffold (structure, uv, config, health endpoint) ✓ checkpoint
- Stage B: Document parser (PDF/DOCX → clean text)          ✓ checkpoint
- Stage C: Chunker + embedder + ChromaDB ingestion          ✓ checkpoint
- Stage D: Retrieval + BGE re-ranking                        ✓ checkpoint
- Stage E: LLM clients (Ollama + Claude, switchable)         ✓ checkpoint
- Stage F: RAG pipeline + FastAPI endpoints (streaming)      ✓ checkpoint
- Stage G: React chat UI (upload, chat, citations)           ✓ checkpoint
- Stage H: README + LICENSE + CI + tests                     ✓ checkpoint
- Stage I: Deploy to Render + screenshots + push             ✓ checkpoint

At each checkpoint: report what was done, confirm it runs, WAIT for green light.

## What NOT to do
- Do not use localStorage/sessionStorage anywhere.
- Do not hardcode secrets or API keys.
- Do not push to git without approval.
- Do not skip the re-ranking step (it's what makes retrieval quality good).
- Do not let the LLM answer outside the retrieved context.
