# VEM AI Accounting Classification Agent

AI-powered prototype for classifying ICT products into Line of Business (LOB) accounting codes.

## Architecture

Three-node LangGraph pipeline:

1. **DB Lookup** — exact match in training data
2. **Web Enrichment** — Tavily search + Qwen3-8B summarization
3. **RAG Classification** — dual ChromaDB retrieval + Qwen3-8B JSON classification

## Prerequisites

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12+ | |
| Ollama | latest | `brew install ollama` |
| qwen3:8b | — | `ollama pull qwen3:8b` |
| Tavily API key | — | [tavily.com](https://tavily.com) |

Data files must exist under `data/`:

- `lob_codes.csv` — LOB taxonomy
- `rag_input_dataset.csv` — article-LOB associations

## Installation

### 1. Create virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create `.env`:

```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx
```

### 4. Start Ollama and pull the model

```bash
# Start the server (keep running in background)
ollama serve

# In another terminal
ollama pull qwen3:8b
```

**Optional — speed optimizations for Apple Silicon (Ollama ≥ 0.4):**

Add to `~/.zshrc` before starting `ollama serve`:

```bash
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
```

### 5. Build the vector store

Built automatically on first `python main.py` run. No manual step needed.

## Usage

### CLI

```bash
python main.py CP-PWR-7920-CE
```

### API Server

```bash
python main.py serve
```

Endpoints:

- `POST /classify` — `{"article_code": "CP-PWR-7920-CE"}`
- `GET /health`
- `GET /lob-codes`

Example:

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"article_code": "CP-PWR-7920-CE"}'
```

### Evaluation Notebook

```bash
jupyter notebook notebooks/evaluation.ipynb
```

Run all cells. Set `SAMPLE_SIZE = 100` (default) for a quick run or increase for full coverage.

## Tests

```bash
python -m pytest tests/agentic_rag/ -v
```

## Configuration

All constants in `src/config.py`. Key settings:

| Variable | Default | Description |
| --- | --- | --- |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model name |
| `OLLAMA_NUM_CTX` | `4096` | Context window (tokens) |
| `OLLAMA_NUM_PREDICT` | `512` | Max output tokens |
| `OLLAMA_TEMPERATURE` | `0.1` | Sampling temperature |
| `TOP_K_ASSOCIATIONS` | `15` | Historical articles retrieved |
| `TOP_K_LOB` | `10` | LOB codes retrieved |
| `FINAL_TOP_N` | `3` | Suggestions returned |
| `TEST_SPLIT_RATIO` | `0.15` | Held-out eval fraction |
