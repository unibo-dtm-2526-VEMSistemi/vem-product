from __future__ import annotations

import os

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TAVILY_MAX_RESULTS,
)
from state import AgentState

_SYSTEM_PROMPT = (
    "/no_think\n"
    "Sei un assistente esperto di prodotti ICT per VEM Sistemi, system integrator italiano. "
    "Ricevi risultati di una ricerca web su un prodotto o servizio ICT. "
    "Scrivi una descrizione chiara, completa e leggibile in italiano, pensata per aiutare "
    "un operatore aziendale a capire di cosa si tratta e a classificarlo. "
    "Includi: cosa fa il prodotto, categoria tecnologica (es. switch di rete, licenza software, "
    "firewall, telefono IP, servizio cloud…), brand principale, e se è un bene fisico durevole, "
    "licenza, servizio o abbonamento. "
    "Scrivi 2-4 frasi di testo discorsivo in italiano. Nessun elenco puntato. Nessun formato "
    "chiave-valore. Nessun preambolo. Inizia direttamente con la descrizione."
)


def _build_search_query(description: str, brand_vendor: str) -> str:
    if brand_vendor:
        return f"{brand_vendor} {description}"
    return description


def _format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        content = r.get("content", "")
        lines.append(f"{i}. {title}: {content[:300]}")
    return "\n".join(lines)


def web_enrichment_node(state: AgentState) -> dict:
    """Node 2: Enrich article with Tavily web search + LLM summarization."""
    article_info = state["article_info"]
    description = article_info["descrizione_articolo"]
    brand = article_info.get("brand_vendor", "")

    try:
        tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))
        query = _build_search_query(description, brand)
        search_response = tavily.search(
            query=query, max_results=TAVILY_MAX_RESULTS, timeout=8
        )
        results = search_response.get("results", [])
        formatted = _format_results(results)

        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            reasoning=False,
            temperature=0.1,
            num_ctx=4096,
        )

        user_message = (
            f"Product: {description}\n\nSearch results:\n{formatted}\n\n/no_think"
        )
        response = llm.invoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
        )

        enrichment = response.content.strip()
        return {"web_enrichment": enrichment}

    except Exception as exc:
        print(f"[web_enrichment] Error: {exc}")
        return {"web_enrichment": "No external information available."}
