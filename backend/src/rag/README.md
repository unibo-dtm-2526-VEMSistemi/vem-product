# RAG Module Contract

This module is aligned with the challenge brief:
- consultative assistant only (no ERP writes)
- local model execution
- guidance on chart-of-accounts classification
- guidance on inventory vs non-inventory treatment
- concise explanation and traceability

## Response Contract

`RagAnswer`:
- `decision.accountCode`
- `decision.accountName`
- `decision.inventoryDecision`
- `explanation`
- `confidence`
- `citations[]`
- `generatedAt`

## Pipeline

1. Ingest internal data (`chart-of-accounts`, `articles`) and external web enrichment cache.
2. Retrieve top-k context chunks.
3. Ask local LLM with strict JSON output prompt.
4. Return decision with citations for traceability.

