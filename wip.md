# WIP: VEM AI Accounting Classification Agent

## Branch
`feat/rag-model`

## Plan file
`docs/superpowers/plans/2026-04-13-vem-rag-agent.md`

## Module layout
```
backend/src/agentic_rag/     ← module root
  src/
    __init__.py
    config.py
    state.py
    data_loader.py
    confidence.py            ← NOT YET CREATED
    vectorstore_setup.py     ← NOT YET CREATED
    graph.py                 ← NOT YET CREATED
    api.py                   ← NOT YET CREATED
    nodes/
      __init__.py
      db_lookup.py           ← NOT YET CREATED
      web_enrichment.py      ← NOT YET CREATED
      rag_classification.py  ← NOT YET CREATED
  main.py                    ← NOT YET CREATED
  requirements.txt
  README.md                  ← NOT YET CREATED
  notebooks/
    evaluation.ipynb         ← NOT YET CREATED

backend/tests/agentic_rag/
  __init__.py
  conftest.py                ← sys.path insert so `from src.xxx import yyy` works
  test_config.py             ✅
  test_state.py              ✅
  test_data_loader.py        ✅
  test_confidence.py         ← NOT YET CREATED
  test_vectorstore_setup.py  ← NOT YET CREATED
  test_graph.py              ← NOT YET CREATED
  test_api.py                ← NOT YET CREATED
  nodes/
    __init__.py
    test_db_lookup.py        ← NOT YET CREATED
    test_web_enrichment.py   ← NOT YET CREATED
    test_rag_classification.py ← NOT YET CREATED
```

## Completed tasks (committed)

| Task | Commit | Tests |
|------|--------|-------|
| Task 1: Project skeleton, config, requirements | `746ae07` | 5 pass |
| Task 2: State definition | `9dab0f4` + `a3aed33` | 2 pass |
| Task 3: Data loader | `934b1c1` | 7 pass |

## Open issues
- None blocking. Code quality review for Task 3 was interrupted by a rate limit error. The spec review passed ✅ and 7/7 tests pass — safe to proceed.

## Next step: Task 4 — Confidence scoring

Use **subagent-driven development** (fresh subagent per task, then spec review, then code quality review).

### Dispatch implementer with this task text:

**Files:**
- Create: `backend/src/agentic_rag/src/confidence.py`
- Create: `backend/tests/agentic_rag/test_confidence.py`

**Tests to write first (`test_confidence.py`):**
```python
import pytest
from src.confidence import compute_confidence

def test_perfect_match():
    result = compute_confidence(llm_confidence=100, cosine_distance=0.0, all_distances=[0.0, 0.5, 1.0])
    assert result == 1.0

def test_worst_match():
    result = compute_confidence(llm_confidence=0, cosine_distance=2.0, all_distances=[0.0, 1.0, 2.0])
    assert result == 0.0

def test_mid_range():
    result = compute_confidence(llm_confidence=50, cosine_distance=1.0, all_distances=[0.0, 1.0, 2.0])
    assert result == 0.5

def test_all_distances_equal():
    result = compute_confidence(llm_confidence=80, cosine_distance=0.3, all_distances=[0.3, 0.3, 0.3])
    assert result == 0.65  # 0.5*0.5 + 0.5*0.8

def test_result_is_rounded_to_4_decimals():
    result = compute_confidence(llm_confidence=73, cosine_distance=0.3, all_distances=[0.1, 0.3, 0.8])
    assert isinstance(result, float)
    assert result == round(result, 4)

def test_penalty_for_hallucinated_code():
    result = compute_confidence(llm_confidence=60, cosine_distance=1.8, all_distances=[0.2, 0.5, 1.0, 1.8])
    assert result == 0.3
```

**Implementation (`confidence.py`):**
```python
def compute_confidence(llm_confidence: int, cosine_distance: float, all_distances: list[float]) -> float:
    """Composite confidence: 0.5 * normalized_cosine + 0.5 * normalized_llm
    ChromaDB cosine space distances in [0, 2]. similarity = 1 - distance.
    """
    similarity = 1.0 - cosine_distance
    all_similarities = [1.0 - d for d in all_distances]
    sim_min = min(all_similarities)
    sim_max = max(all_similarities)
    if sim_max == sim_min:
        normalized_cosine = 0.5
    else:
        normalized_cosine = (similarity - sim_min) / (sim_max - sim_min)
    normalized_llm = llm_confidence / 100.0
    return round(0.5 * normalized_cosine + 0.5 * normalized_llm, 4)
```

**Run tests:** `cd backend && /Library/Frameworks/Python.framework/Versions/3.13/bin/pytest tests/agentic_rag/test_confidence.py -v`
Expected: 6 PASSED

**Commit:** `git commit -m "feat: confidence score computation"`

## Remaining tasks after Task 4

- Task 5: `src/vectorstore_setup.py` + `test_vectorstore_setup.py` (ChromaDB, 2 collections, skip if populated, force_rebuild)
- Task 6: `src/nodes/db_lookup.py` + `nodes/test_db_lookup.py`
- Task 7: `src/nodes/web_enrichment.py` + `nodes/test_web_enrichment.py` (Tavily + ChatOllama /no_think)
- Task 8: `src/nodes/rag_classification.py` + `nodes/test_rag_classification.py` (parse_qwen3_json, dual ChromaDB query, /think)
- Task 9: `src/graph.py` + `test_graph.py` (LangGraph StateGraph, classify_article)
- Task 10: `src/api.py` + `test_api.py` (FastAPI, lifespan, /classify /health /lob-codes)
- Task 11: `src/agentic_rag/main.py` (CLI + serve mode)
- Task 12: `notebooks/evaluation.ipynb` (7 cells)
- Task 13: `README.md`
- Task 14: Full test suite smoke test

## How to run tests
```bash
cd backend
/Library/Frameworks/Python.framework/Versions/3.13/bin/pytest tests/agentic_rag/ -v
```

## Key technical notes
- `from src.xxx import yyy` import style (not `from agentic_rag.src.xxx`)
- conftest.py at `backend/tests/agentic_rag/conftest.py` sets up sys.path
- Subagent-driven dev: implementer → spec review (general-purpose agent) → code quality review (superpowers:code-reviewer)
- All task code is in the plan file — paste full task text when dispatching implementers
