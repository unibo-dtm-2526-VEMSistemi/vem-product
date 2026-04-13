# VEM AI Accounting Classification Agent

AI-powered prototype for classifying ICT products into Line of Business (LOB) accounting codes.

## Architecture

Three-node LangGraph pipeline:
1. **DB Lookup** — exact match in training data  
2. **Web Enrichment** — Tavily search + Qwen3-8B summarization (no-think mode)  
3. **RAG Classification** — dual ChromaDB retrieval + Qwen3-8B reasoning (think mode)

## Prerequisites

- Python 3.12+
- Ollama running at `http://localhost:11434` with `qwen3:8b` pulled: `ollama pull qwen3:8b`
- Environment variable: `TAVILY_API_KEY=<your-key>`
- Data files in `data/`:
  - `lob_codes.csv` — LOB taxonomy (319 rows)
  - `rag_input_dataset.csv` — article-LOB associations (~20,499 rows)

## Setup

```bash
cd backend/src/agentic_rag
pip install -r requirements.txt
```

## Usage

### CLI

```bash
cd backend/src/agentic_rag
python main.py CP-PWR-7920-CE
```

### API Server

```bash
cd backend/src/agentic_rag
python main.py serve
```

Endpoints:
- `POST /classify` — `{"article_code": "CP-PWR-7920-CE"}`
- `GET /health`
- `GET /lob-codes`

### Evaluation Notebook

```bash
cd backend/src/agentic_rag
jupyter notebook notebooks/evaluation.ipynb
```

Run all cells. Set `SAMPLE_SIZE = 100` (default) for a quick evaluation or increase for more coverage.

## Tests

```bash
cd backend
python -m pytest tests/agentic_rag/ -v
```

## Configuration

All constants are in `src/config.py`. Key settings:
- `TOP_K_ASSOCIATIONS = 15` — number of historical articles retrieved
- `TOP_K_LOB = 10` — number of LOB codes retrieved  
- `FINAL_TOP_N = 3` — number of suggestions returned
- `TEST_SPLIT_RATIO = 0.15` — 15% held out for evaluation
