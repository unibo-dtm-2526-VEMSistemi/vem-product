# AGENTS.md

Guide for AI coding agents working on this codebase.

---

## Project Overview

**VEM Product** is an AI-powered accounting classification system for ICT products, built for VEM Sistemi (Italian company). Given an article code, it returns ranked LOB (Line of Business) classification suggestions with confidence scores.

The pipeline runs as a LangGraph agent with three sequential nodes:

```
db_lookup → web_enrichment → rag_classification
```

| Node | Role |
|------|------|
| `db_lookup` | Exact-match lookup in training dataset |
| `web_enrichment` | Tavily web search to enrich article description |
| `rag_classification` | ChromaDB retrieval + Ollama LLM for ranked suggestions |

The system exposes a FastAPI REST API. The entry point is `main.py`; source lives in `src/`.

---

## Repository Structure

```
.
├── main.py                     # CLI entrypoint (serve or classify)
├── src/
│   ├── api.py                  # FastAPI app + endpoints
│   ├── graph.py                # LangGraph pipeline definition
│   ├── state.py                # AgentState TypedDict
│   ├── config.py               # All configuration constants (loaded from .env)
│   ├── confidence.py           # Composite confidence score formula
│   ├── data_loader.py          # CSV loading, train/test split, article lookup
│   ├── vectorstore_setup.py    # ChromaDB collections init and access
│   └── nodes/
│       ├── db_lookup.py        # Node 1: dataset lookup
│       ├── web_enrichment.py   # Node 2: Tavily web search + LLM summarisation
│       └── rag_classification.py # Node 3: RAG retrieval + LLM classification
├── tests/
│   ├── conftest.py             # sys.path setup (adds src/ for bare imports)
│   ├── nodes/                  # Unit tests for each node
│   └── *.py                    # Unit tests for each src module
├── data/
│   ├── lob_codes.csv           # LOB taxonomy (code + name)
│   └── rag_input_dataset.csv   # Labelled articles for RAG and training
└── vectorstore/                # ChromaDB persistence directory (gitignored)
```

---

## Environment Setup

Requires Python 3.12+, Ollama running locally, and a `.env` file in the project root.

```bash
pip install -r requirements.txt
```

**`.env` variables (all optional — defaults are in `src/config.py`):**

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
TAVILY_API_KEY=<your_key>
```

Ollama performance tip: set `OLLAMA_FLASH_ATTENTION=1` and `OLLAMA_KV_CACHE_TYPE=q8_0` in your shell environment.

---

## Build & Run Commands

```bash
# Start API server (port 8000)
python main.py serve

# Classify a single article via CLI
python main.py ART-001

# Run all tests
python3 -m pytest tests/ -v

# Run tests with coverage
python3 -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## Testing

- All tests live in `tests/`. Node-specific tests are in `tests/nodes/`.
- `tests/conftest.py` adds `src/` to `sys.path` so internal bare imports resolve. Do not remove this.
- Tests use `unittest.mock` — no real files, no real Ollama, no real ChromaDB, no real Tavily calls.
- `data_loader.load_datasets` uses `@functools.lru_cache`. Always call `data_loader.load_datasets.cache_clear()` before patching `pd.read_csv` in tests.
- Import `app` as `from src.api import app`, never via `sys.path` hacks. Patching must target `src.api.*` not `api.*`.
- When creating `TestClient(app)` inside a `with patch(...)` block, the patches apply to the lifespan startup. Create the client inside the block for tests that need startup mocks.

**Current coverage:** 99% (`src/api.py` lifespan lines excluded — they run only at app startup and are covered by integration-level patching).

---

## Code Style

- Python 3.12+. Type hints on all function signatures. `from __future__ import annotations` at top of every file.
- Imports inside node functions are fine (they avoid circular imports at module load).
- `AgentState` is a `TypedDict` in `src/state.py`. Nodes receive the full state and return only the keys they modify as a `dict`.
- Configuration constants come from `src/config.py`. Do not hardcode values like model names, paths, or thresholds anywhere else.
- No inline comments unless the WHY is non-obvious. No docstrings unless the function is a public API boundary.

---

## Architecture Constraints

- **Node contract:** each node function has signature `(state: AgentState) -> dict`. Return only the keys the node modifies — LangGraph merges the dict into state.
- **Graph entry point:** `db_lookup`. If `article_info` is `None` after lookup, the graph routes directly to `END` via the `should_continue` conditional edge.
- **ChromaDB collections:** two collections — `lob_codes` (LOB taxonomy) and `article_associations` (labelled articles). Access via `vectorstore_setup.get_collections()`.
- **Embedding model:** `paraphrase-multilingual-MiniLM-L12-v2` (multilingual, handles Italian product descriptions).
- **LLM:** Ollama `qwen3:8b` with `temperature=0.1` and `num_ctx=4096`. The LLM output is JSON-only — `parse_qwen3_json` in `rag_classification.py` strips `<think>` tags and markdown fences before parsing.
- **Confidence score:** composite of normalized cosine similarity (0.5 weight) and LLM self-reported confidence (0.5 weight), rounded to 4 decimals. Formula in `src/confidence.py`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/classify` | Classify an article. Body: `{"article_code": "ART-001"}` |
| `GET` | `/health` | Health check. Returns `{"status": "ok", "model": "<model>"}` |
| `GET` | `/lob-codes` | Full LOB taxonomy as list of records |

`POST /classify` returns 404 if the article is not found in the dataset and no suggestions were produced.

---

## Data Files

- `data/lob_codes.csv`: columns `LOB Code`, `Name`. LOB codes are zero-padded to 5 digits (e.g. `02002`).
- `data/rag_input_dataset.csv`: must have `codice_articolo`, `lob_associata_cleaned`, `rag_text`, `inventario`, `brand_vendor`, `product_family`. Rows with empty/NaN `rag_text` are dropped at load time.
- Do not modify data files in code. They are loaded read-only via `data_loader.load_datasets()`.

---

## Security

- `TAVILY_API_KEY` must be in `.env`, never committed.
- `.env` is in `.gitignore`. Verify before any commit touching configuration.
- The API has no authentication. Do not expose port 8000 publicly without a reverse proxy and auth layer.
