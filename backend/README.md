# Backend RAG Skeleton

This folder hosts the backend side of the VEM assistant.

Current focus:
- local LLM + RAG architecture
- consultative workflow for accounting classification
- traceable outputs (accounting code suggestion + inventory guidance + explanation + citations)

Directory overview:
- `main.py`: FastAPI app used for local backend runtime
- `src/rag/`: RAG modules (ingestion, retrieval, llm, service, api)
- `data/internal/chart-of-accounts/`: chart of accounts source files
- `data/internal/articles/`: purchased/sold items source files
- `data/external/web-cache/`: normalized web enrichment cache

Setup and run:
1. `npm run setup:backend`
2. `npm run dev:backend`

Expected next steps:
1. Connect real data loaders in `src/rag/ingestion/`.
2. Plug a vector database in `src/rag/retrieval/`.
3. Configure a local model endpoint in `src/rag/llm/`.
4. Expose HTTP endpoints from `src/rag/api/`.
