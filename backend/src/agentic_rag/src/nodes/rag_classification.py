from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
    OLLAMA_NUM_CTX,
    TOP_K_ASSOCIATIONS,
    TOP_K_LOB,
    FINAL_TOP_N,
)
from src.confidence import compute_confidence
from src.state import AgentState
from src.vectorstore_setup import get_collections, _get_embedding_function

_SYSTEM_PROMPT = """\
Sei un esperto agente di classificazione contabile per un'azienda italiana ICT (VEM Sistemi). \
Il tuo compito è classificare un prodotto/articolo nel corretto codice Line of Business (LOB) \
e determinare il suo trattamento a magazzino.

In base alle informazioni sul prodotto e ai dati di riferimento recuperati, fornisci esattamente \
3 suggerimenti di classificazione ordinati per confidenza.

Devi rispondere SOLO con JSON valido, nessun altro testo fuori dal JSON. \
Usa esattamente questa struttura:
{
  "classifications": [
    {
      "lob_code": "il codice LOB (es. 02002)",
      "lob_name": "il nome del LOB",
      "inventory": "uno tra: Inventario, Non in inventario",
      "explanation": "1-2 frasi che spiegano perché questa classificazione è corretta, \
citando prove dal contesto, scritte in italiano",
      "llm_confidence": intero da 0 a 100
    }
  ]
}

Regole:
- lob_code e lob_name DEVONO provenire dai codici LOB nel contesto.
- inventory DEVE essere esattamente "Inventario" o "Non in inventario".
- llm_confidence: 100 = prova inequivocabile; sotto 30 = ipotesi. Valuta quanto i documenti \
recuperati supportano questa classificazione.
- 3 suggerimenti ordinati da confidenza più alta a più bassa.
- Fai riferimento a prodotti simili o descrizioni LOB nelle tue spiegazioni.
- Scrivi l'explanation in italiano.
"""


def parse_qwen3_json(raw_output: str) -> dict:
    """Extract JSON from Qwen3 output that may contain <think>...</think> and markdown fences."""
    text = raw_output

    # Strip <think>...</think> — keep only content after last </think>
    if "</think>" in text:
        text = text[text.rfind("</think>") + len("</think>"):]

    # Strip markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse JSON from LLM output: {exc}\nRaw: {text[:500]}")


def _infer_inventory_filter(web_enrichment: str) -> str | None:
    """Return metadata filter value if enrichment clearly indicates hardware/software."""
    lower = web_enrichment.lower()
    hardware_signals = {"hardware", "fisico", "physical", "appliance", "device", "dispositivo", "asset durevole"}
    software_signals = {"software", "licenza", "license", "subscription", "abbonamento", "saas", "cloud"}

    has_hardware = any(s in lower for s in hardware_signals)
    has_software = any(s in lower for s in software_signals)

    if has_hardware and not has_software:
        return "Inventario"
    if has_software and not has_hardware:
        return "Non in inventario"
    return None


def _embed_query(query: str) -> list[float]:
    """Embed query string using the module-level embedding function."""
    ef = _get_embedding_function()
    return ef([query])[0]


def _build_context(assoc_results: dict, lob_results: dict) -> tuple[str, list[float]]:
    """Build the context block for the LLM and collect all distances."""
    assoc_metadatas = assoc_results.get("metadatas", [[]])[0]
    assoc_distances = assoc_results.get("distances", [[]])[0]
    lob_metadatas = lob_results.get("metadatas", [[]])[0]
    lob_distances = lob_results.get("distances", [[]])[0]

    # Deduplicate associations by LOB code, keeping best (lowest distance)
    seen_lobs: dict[str, tuple[dict, float]] = {}
    for meta, dist in zip(assoc_metadatas, assoc_distances):
        code = meta.get("lob_code_str", "")
        if code not in seen_lobs or dist < seen_lobs[code][1]:
            seen_lobs[code] = (meta, dist)

    all_distances = [d for _, d in seen_lobs.values()] + list(lob_distances)

    lines = ["=== CLASSIFICAZIONI STORICHE SIMILI ==="]
    for i, (meta, dist) in enumerate(seen_lobs.values(), 1):
        sim = round(1.0 - dist, 3)
        lines.append(
            f"{i}. Articolo: {meta.get('descrizione_articolo', '')} → "
            f"LOB: {meta.get('lob_code_str', '')} - {meta.get('lob_nome', '')} | "
            f"Inventario: {meta.get('inventario', '')} (similarity: {sim})"
        )

    lines.append("\n=== CODICI LOB DISPONIBILI (più rilevanti) ===")
    for i, (meta, dist) in enumerate(zip(lob_metadatas, lob_distances), 1):
        sim = round(1.0 - dist, 3)
        lines.append(f"{i}. {meta.get('lob_code', '')} - {meta.get('name', '')} (similarity: {sim})")

    return "\n".join(lines), all_distances


def _call_llm_with_retry(llm: ChatOllama, messages: list, state: AgentState) -> dict:
    """Call LLM, retry once with simplified prompt on JSON parse failure."""
    for attempt in range(2):
        try:
            response = llm.invoke(messages)
            return parse_qwen3_json(response.content)
        except (ValueError, Exception) as exc:
            if attempt == 0:
                print(f"[rag_classification] Attempt 1 failed ({exc}), retrying...")
                # Simplified retry prompt
                article_info = state["article_info"]
                simple_user = (
                    f"Classifica questo articolo ICT: {article_info['descrizione_articolo']}\n"
                    f"Rispondi SOLO con JSON valido con chiave 'classifications' contenente "
                    f"esattamente 3 oggetti con campi: lob_code, lob_name, inventory, explanation, llm_confidence."
                )
                messages = [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=simple_user)]
            else:
                raise


def rag_classification_node(state: AgentState) -> dict:
    """Node 3: RAG retrieval + LLM classification."""
    t_node_start = time.perf_counter()
    timings: dict[str, float] = {}

    article_info = state["article_info"]
    web_enrichment = state.get("web_enrichment", "")

    # Step A: Build query
    t0 = time.perf_counter()
    parts = []
    if article_info.get("brand_vendor"):
        parts.append(article_info["brand_vendor"])
    if article_info.get("product_family"):
        parts.append(article_info["product_family"])
    parts.append(article_info["descrizione_articolo"])
    if web_enrichment and web_enrichment != "No external information available.":
        parts.append(web_enrichment)
    query = " ".join(parts)
    timings["A_build_query"] = time.perf_counter() - t0

    try:
        t0 = time.perf_counter()
        lob_col, assoc_col = get_collections()
        timings["B1_get_collections"] = time.perf_counter() - t0

        # Step B: Single embedding, dual collection query
        t0 = time.perf_counter()
        embedding = _embed_query(query)
        timings["B2_embed_query"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        inventory_filter = _infer_inventory_filter(web_enrichment)
        where_filter = {"inventario": inventory_filter} if inventory_filter else None

        assoc_query_kwargs = {
            "query_embeddings": [embedding],
            "n_results": TOP_K_ASSOCIATIONS,
            "include": ["metadatas", "distances"],
        }
        if where_filter:
            assoc_query_kwargs["where"] = where_filter

        lob_query_kwargs = {
            "query_embeddings": [embedding],
            "n_results": TOP_K_LOB,
            "include": ["metadatas", "distances"],
        }
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_assoc = pool.submit(assoc_col.query, **assoc_query_kwargs)
            f_lob = pool.submit(lob_col.query, **lob_query_kwargs)
            assoc_results = f_assoc.result()
            lob_results = f_lob.result()
        timings["B3_vector_search"] = time.perf_counter() - t0

        # Steps C + D: Build context (deduplication happens inside)
        t0 = time.perf_counter()
        context_block, all_distances = _build_context(assoc_results, lob_results)
        timings["CD_build_context"] = time.perf_counter() - t0

        # Step E: Call LLM
        t0 = time.perf_counter()
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            reasoning=False,
            temperature=OLLAMA_TEMPERATURE,
            top_p=0.9,
            top_k=20,
            num_ctx=OLLAMA_NUM_CTX,
            num_thread=8,
            num_gpu=99,
        )

        user_message = (
            f"Codice articolo: {article_info['codice_articolo']}\n"
            f"Descrizione: {article_info['descrizione_articolo']}\n"
            f"Brand/Vendor: {article_info.get('brand_vendor', 'N/A')}\n"
            f"Famiglia prodotto: {article_info.get('product_family', 'N/A')}\n"
            f"Informazioni web: {web_enrichment or 'N/A'}\n\n"
            f"{context_block}"
        )

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        # Steps F: Parse with retry
        parsed = _call_llm_with_retry(llm, messages, state)
        timings["EF_llm_call"] = time.perf_counter() - t0
        classifications_raw = parsed.get("classifications", [])

        # Step G: Compute confidence
        t0 = time.perf_counter()
        lob_distances_map: dict[str, float] = {}
        assoc_metas = assoc_results.get("metadatas", [[]])[0]
        assoc_dists = assoc_results.get("distances", [[]])[0]
        for meta, dist in zip(assoc_metas, assoc_dists):
            code = meta.get("lob_code_str", "")
            if code not in lob_distances_map or dist < lob_distances_map[code]:
                lob_distances_map[code] = dist

        worst_distance = max(all_distances) if all_distances else 2.0

        suggestions = []
        for rank, cls in enumerate(classifications_raw[:FINAL_TOP_N], 1):
            lob_code = cls.get("lob_code", "")
            cosine_dist = lob_distances_map.get(lob_code, worst_distance)
            confidence = compute_confidence(
                llm_confidence=cls.get("llm_confidence", 0),
                cosine_distance=cosine_dist,
                all_distances=all_distances,
            )
            suggestions.append({
                "rank": rank,
                "lob_code": lob_code,
                "lob_name": cls.get("lob_name", ""),
                "inventory": cls.get("inventory", ""),
                "explanation": cls.get("explanation", ""),
                "confidence": confidence,
            })
        suggestions.sort(key=lambda x: x.get('confidence'), reverse=True)
        for idx, s in enumerate(suggestions):
            s["rank"] = idx + 1
        timings["G_confidence"] = time.perf_counter() - t0

        total = time.perf_counter() - t_node_start
        print("[rag_classification] step timings (s):")
        for step, elapsed in timings.items():
            print(f"  {step:<22} {elapsed:.3f}s")
        print(f"  {'TOTAL':<22} {total:.3f}s")

        return {
            "classification": suggestions,
            "retrieval_results": [
                {"lob_code": m.get("lob_code_str", ""), "distance": d}
                for m, d in zip(assoc_metas, assoc_dists)
            ],
        }

    except Exception as exc:
        print(f"[rag_classification] Fatal error: {exc}")
        return {
            "classification": [],
            "error": f"Classification failed: {exc}",
        }
