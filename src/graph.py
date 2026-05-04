from __future__ import annotations

import time

from langgraph.graph import StateGraph, END

from state import AgentState
from nodes.db_lookup import db_lookup_node
from nodes.web_enrichment import web_enrichment_node
from nodes.rag_classification import rag_classification_node


def should_continue(state: AgentState) -> str | list[str]:
    """Conditional edge: stop if article not found, else fan out to both nodes in parallel."""
    if state.get("article_info") is None:
        return "end"
    return ["web_enrichment", "rag_classification"]


def _timed(name: str, fn):
    def wrapper(state):
        t0 = time.perf_counter()
        result = fn(state)
        print(f"[timing] {name}: {time.perf_counter() - t0:.2f}s")
        return result

    return wrapper


def _db_lookup_wrapper(state: AgentState) -> dict:
    return _timed("db_lookup", db_lookup_node)(state)


def _web_enrichment_wrapper(state: AgentState) -> dict:
    return _timed("web_enrichment", web_enrichment_node)(state)


def _rag_classification_wrapper(state: AgentState) -> dict:
    return _timed("rag_classification", rag_classification_node)(state)


def _build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("db_lookup", _db_lookup_wrapper)
    workflow.add_node("web_enrichment", _web_enrichment_wrapper)
    workflow.add_node("rag_classification", _rag_classification_wrapper)

    workflow.set_entry_point("db_lookup")
    workflow.add_conditional_edges(
        "db_lookup",
        should_continue,
        {
            "end": END,
            "web_enrichment": "web_enrichment",
            "rag_classification": "rag_classification",
        },
    )
    workflow.add_edge("web_enrichment", END)
    workflow.add_edge("rag_classification", END)

    return workflow.compile()


_graph = _build_graph()


def classify_article(article_code: str) -> dict:
    """Run the full classification pipeline for an article code."""
    initial_state: AgentState = {
        "article_code": article_code,
        "article_info": None,
        "web_enrichment": "",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }

    final_state = _graph.invoke(initial_state)

    article_info = final_state.get("article_info")
    print()

    if article_info is None:
        return {
            "article_code": article_code,
            "article_description": None,
            "description": None,
            "suggestions": [],
            "error": final_state.get("error"),
        }

    return {
        "article_code": article_code,
        "article_description": article_info.get("descrizione_articolo"),
        "description": final_state.get("web_enrichment"),
        "suggestions": final_state.get("classification", []),
        "error": final_state.get("error"),
    }
