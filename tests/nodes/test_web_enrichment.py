import pytest
from unittest.mock import patch, MagicMock


MOCK_STATE = {
    "article_code": "ART-001",
    "article_info": {
        "codice_articolo": "ART-001",
        "descrizione_articolo": "CISCO SWITCH 24P",
        "lob_code_str": "02002",
        "lob_nome": "APPARATI CISCO LAN",
        "inventario": "Inventario",
        "brand_vendor": "CISCO",
        "product_family": "SWITCH",
    },
    "web_enrichment": "",
    "retrieval_results": [],
    "classification": [],
    "error": None,
}


def test_web_enrichment_success():
    """Happy path: Tavily returns results, LLM summarizes them."""
    from src.nodes.web_enrichment import web_enrichment_node

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"title": "Cisco Switch", "content": "A network hardware device.", "url": "http://example.com"}
        ]
    }

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="Hardware: switch di rete Cisco, asset durevole.")

    with patch("src.nodes.web_enrichment.TavilyClient", return_value=mock_tavily), \
         patch("src.nodes.web_enrichment.ChatOllama", return_value=mock_llm):
        result = web_enrichment_node(MOCK_STATE)

    assert "web_enrichment" in result
    assert len(result["web_enrichment"]) > 0
    assert result.get("error") is None


def test_web_enrichment_tavily_failure():
    """When Tavily raises an exception, fall back gracefully."""
    from src.nodes.web_enrichment import web_enrichment_node

    mock_tavily = MagicMock()
    mock_tavily.search.side_effect = Exception("Tavily API error")

    with patch("src.nodes.web_enrichment.TavilyClient", return_value=mock_tavily):
        result = web_enrichment_node(MOCK_STATE)

    assert result["web_enrichment"] == "No external information available."
    # Pipeline must not crash
    assert "error" not in result or result.get("error") is None


def test_web_enrichment_query_includes_brand():
    """Search query should include brand_vendor when available."""
    from src.nodes.web_enrichment import _build_search_query

    query = _build_search_query("SWITCH 24P", "CISCO")
    assert "CISCO" in query
    assert "SWITCH 24P" in query


def test_web_enrichment_query_no_brand():
    """When brand is empty, query is just the description."""
    from src.nodes.web_enrichment import _build_search_query

    query = _build_search_query("SWITCH 24P", "")
    assert "SWITCH 24P" in query


def test_web_enrichment_llm_failure_fallback():
    """When LLM fails after Tavily success, return graceful fallback."""
    from src.nodes.web_enrichment import web_enrichment_node

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [{"title": "Test", "content": "content", "url": "http://x.com"}]
    }

    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = Exception("LLM error")

    with patch("src.nodes.web_enrichment.TavilyClient", return_value=mock_tavily), \
         patch("src.nodes.web_enrichment.ChatOllama", return_value=mock_llm):
        result = web_enrichment_node(MOCK_STATE)

    assert result["web_enrichment"] == "No external information available."
