import pytest
from unittest.mock import patch, MagicMock


def test_classify_article_found():
    """Full pipeline for a known article returns suggestions."""
    from src.graph import classify_article

    mock_db_result = {
        "article_info": {
            "codice_articolo": "ART-001",
            "descrizione_articolo": "CISCO SWITCH 24P",
            "lob_code_str": "02002",
            "lob_nome": "APPARATI CISCO LAN",
            "inventario": "Inventario",
            "brand_vendor": "CISCO",
            "product_family": "SWITCH",
        },
        "error": None,
    }
    mock_web_result = {"web_enrichment": "Hardware: switch Cisco."}
    mock_rag_result = {
        "classification": [
            {"rank": 1, "lob_code": "02002", "lob_name": "APPARATI CISCO LAN",
             "inventory": "Inventario", "explanation": "Switch Cisco.", "confidence": 0.88},
            {"rank": 2, "lob_code": "04001", "lob_name": "TELEFONIA IP",
             "inventory": "Inventario", "explanation": "Telefonia.", "confidence": 0.55},
            {"rank": 3, "lob_code": "01001", "lob_name": "CABLAGGI",
             "inventory": "Inventario", "explanation": "Cablaggi.", "confidence": 0.30},
        ],
        "retrieval_results": [],
    }

    with patch("src.graph.db_lookup_node", return_value=mock_db_result), \
         patch("src.graph.web_enrichment_node", return_value=mock_web_result), \
         patch("src.graph.rag_classification_node", return_value=mock_rag_result):
        result = classify_article("ART-001")

    assert result["article_code"] == "ART-001"
    assert result["article_description"] == "CISCO SWITCH 24P"
    assert result["existing_lob"] == "02002 - APPARATI CISCO LAN"
    assert result["existing_inventory"] == "Inventario"
    assert len(result["suggestions"]) == 3
    assert result["suggestions"][0]["rank"] == 1
    assert result["error"] is None


def test_classify_article_not_found():
    """Pipeline stops at db_lookup when article not found."""
    from src.graph import classify_article

    mock_db_result = {
        "article_info": None,
        "error": "Article not found in dataset: NOPE",
    }

    with patch("src.graph.db_lookup_node", return_value=mock_db_result):
        result = classify_article("NOPE")

    assert result["article_code"] == "NOPE"
    assert result["suggestions"] == []
    assert result["error"] is not None
    assert "not found" in result["error"].lower()


def test_should_continue_routes_to_end():
    from src.graph import should_continue

    state_no_article = {
        "article_code": "NOPE",
        "article_info": None,
        "web_enrichment": "",
        "retrieval_results": [],
        "classification": [],
        "error": "not found",
    }
    assert should_continue(state_no_article) == "end"


def test_should_continue_routes_to_continue():
    from src.graph import should_continue

    state_with_article = {
        "article_code": "ART-001",
        "article_info": {"codice_articolo": "ART-001"},
        "web_enrichment": "",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }
    assert should_continue(state_with_article) == "continue"
