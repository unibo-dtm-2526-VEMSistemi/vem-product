# VEM Product Assistant

Front-end app for VEM product/accounting assistant, with a new backend skeleton for a local LLM + RAG model.

## Run From Terminal

Install frontend dependencies:

```bash
npm install
```

Setup backend virtual environment and backend dependencies:

```bash
npm run setup:backend
```

Run backend only:

```bash
npm run dev:backend
```

Run frontend only:

```bash
npm run dev:frontend
```

Run backend + frontend together:

```bash
npm run dev
```

## Structure

- `src/`: React UI (chat dashboard and product views)
- `backend/src/rag/`: RAG model modules
- `backend/data/internal/chart-of-accounts/`: company chart of accounts source
- `backend/data/internal/articles/`: sold/purchased items source
- `backend/data/external/web-cache/`: normalized web enrichment cache

## RAG Backend Modules

- `ingestion/`: adapters for internal and external sources
- `retrieval/`: retriever and ranking layer
- `llm/`: local model client (Ollama-compatible endpoint)
- `service/`: accounting advisory orchestration
- `api/`: handler layer for HTTP integration

## Next Step

Implement real loaders in:
- `backend/src/rag/ingestion/chartOfAccountsSource.ts`
- `backend/src/rag/ingestion/productsSource.ts`
- `backend/src/rag/ingestion/webEnrichmentSource.ts`
