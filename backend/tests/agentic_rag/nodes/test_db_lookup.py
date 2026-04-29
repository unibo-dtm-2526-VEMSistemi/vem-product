import pandas as pd
import pytest
from unittest.mock import patch


MOCK_TRAIN_INFO = {
    "codice_articolo": "ART-001",
    "descrizione_articolo": "CISCO SWITCH 24P",
    "lob_code_str": "02002",
    "lob_nome": "APPARATI CISCO LAN",
    "inventario": "Inventario",
    "brand_vendor": "CISCO",
    "product_family": "SWITCH",
}


def test_db_lookup_found():
    """When article is found, article_info is populated and error is None."""
    from src.nodes.db_lookup import db_lookup_node

    state = {
        "article_code": "ART-001",
        "article_info": None,
        "web_enrichment": "",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }

    mock_train_df = pd.DataFrame([{
        "codice_articolo": "ART-001",
        "descrizione_articolo": "CISCO SWITCH 24P",
        "lob_code_str": "02002",
        "lob_nome": "APPARATI CISCO LAN",
        "inventario": "Inventario",
        "brand_vendor": "CISCO",
        "product_family": "SWITCH",
    }])

    with patch("src.nodes.db_lookup.get_train_test_split", return_value=(mock_train_df, pd.DataFrame())), \
         patch("src.nodes.db_lookup.get_article_info", return_value=MOCK_TRAIN_INFO):
        result = db_lookup_node(state)

    assert result["article_info"] is not None
    assert result["article_info"]["codice_articolo"] == "ART-001"
    assert result["article_info"]["lob_code_str"] == "02002"
    assert result["error"] is None


def test_db_lookup_not_found():
    """When article is not found, article_info=None, error is set."""
    from src.nodes.db_lookup import db_lookup_node

    state = {
        "article_code": "NONEXISTENT",
        "article_info": None,
        "web_enrichment": "",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }

    with patch("src.nodes.db_lookup.get_train_test_split", return_value=(pd.DataFrame(), pd.DataFrame())), \
         patch("src.nodes.db_lookup.get_article_info", return_value=None):
        result = db_lookup_node(state)

    assert result["article_info"] is None
    assert result["error"] is not None
    assert "not found" in result["error"].lower()


def test_db_lookup_preserves_other_state_fields():
    """db_lookup_node only modifies article_info and error fields."""
    from src.nodes.db_lookup import db_lookup_node

    state = {
        "article_code": "ART-001",
        "article_info": None,
        "web_enrichment": "existing enrichment",
        "retrieval_results": [{"existing": "result"}],
        "classification": [],
        "error": None,
    }

    with patch("src.nodes.db_lookup.get_train_test_split", return_value=(pd.DataFrame(), pd.DataFrame())), \
         patch("src.nodes.db_lookup.get_article_info", return_value=MOCK_TRAIN_INFO):
        result = db_lookup_node(state)

    # These fields should not be touched by db_lookup
    assert result.get("web_enrichment", "existing enrichment") == "existing enrichment"
