from __future__ import annotations

import os

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient

from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TAVILY_MAX_RESULTS,
)
from src.state import AgentState

_SYSTEM_PROMPT = (
    "Sei un assistente di ricerca prodotti per VEM Sistemi, system integrator ICT italiano. "
    "Ricevi i risultati di una ricerca web su un prodotto/servizio ICT. "
    "Estrai SOLO le informazioni rilevanti per associarlo a un piano dei conti "
    "(chart of account) di VEM. Le LOB di VEM sono organizzate per: "
    "vendor × area-funzionale × natura-commerciale. "
    "Devi quindi identificare tutti e tre questi assi.\n\n"
    "Estrai, quando presenti nei risultati di ricerca:\n"
    "1. VENDOR / BRAND principale (es. Cisco, HP, Microsoft, NetApp, etc). Riporta anche la "
    "sub-brand / linea di prodotto se discriminante (es. 'Cisco Meraki' vs "
    "'Cisco Catalyst' vs 'Cisco Webex').\n"
    "2. AREA FUNZIONALE: una tra {cablaggio strutturato, networking LAN/WAN/Wireless, "
    "data center / server / storage, cloud / virtualizzazione, software / sistema "
    "operativo, collaboration / videoconferenza / telefonia IP, security / "
    "cybersecurity, IoT, building automation / digital building, videosorveglianza, "
    "controllo accessi, servizi internet / connettività / domini, consulenza, "
    "formazione, servizi gestiti / outsourcing, sviluppo software custom}.\n"
    "3. SOTTO-FUNZIONE entro l'area (es. dentro security: firewall NGFW, EDR, "
    "SIEM, web gateway, vulnerability assessment; dentro networking: switch, "
    "AP wireless, router WAN, SD-WAN; dentro storage: backup, iperconvergenza, "
    "object storage).\n"
    "4. FORMA del bene: hardware fisico / appliance / licenza software perpetua / "
    "subscription / SaaS / servizio professionale (consulenza, installazione, "
    "manutenzione) / contratto di supporto vendor (es. Cisco Smartnet, FortiCare, "
    "HPE Support).\n"
    "5. NATURA COMMERCIALE: nuovo acquisto / rinnovo (renewal) / canone ricorrente "
    "/ una-tantum / installazione / prevendita. Se è un rinnovo o renewal di una "
    "licenza/contratto già in uso, segnalalo esplicitamente.\n"
    "6. DURATA / TERMINE contrattuale se indicato (es. 12, 36, 60 mesi; perpetua).\n"
    "7. RILEVANZA INVENTARIALE: durevole/cespite (asset capitalizzabile, vita "
    "utile pluriennale, valore unitario significativo) vs consumabile/fungibile "
    "vs servizio (non inventariabile). Indica vita utile tipica se evidente.\n"
    "8. RUOLO nel sistema: prodotto autonomo vs componente / accessorio / "
    "ricambio / parte di un bundle.\n"
    "Regole di output:\n"
    "- Massimo 6 righe, una informazione per riga, formato 'CHIAVE: valore'.\n"
    "- Se un'informazione non è presente nei risultati, ometti la riga (NON "
    "inventare, NON dire 'non disponibile').\n"
    "- Sii fattuale e conciso. Niente preamboli, niente disclaimer.\n"
    "- Scrivi in italiano. Mantieni in inglese i nomi propri di prodotto/vendor.\n"
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
        search_response = tavily.search(query=query, max_results=TAVILY_MAX_RESULTS, timeout=8)
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
        response = llm.invoke([
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])

        enrichment = response.content.strip()
        return {"web_enrichment": enrichment}

    except Exception as exc:
        print(f"[web_enrichment] Error: {exc}")
        return {"web_enrichment": "No external information available."}
