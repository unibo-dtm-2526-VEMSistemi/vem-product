import pytest
from unittest.mock import patch, MagicMock


def test_parse_qwen3_json_clean():
    """Parse JSON with no think tags."""
    from src.nodes.rag_classification import parse_qwen3_json

    raw = '{"classifications": [{"lob_code": "02002", "lob_name": "APPARATI CISCO LAN", "inventory": "Inventario", "explanation": "test", "llm_confidence": 90}]}'
    result = parse_qwen3_json(raw)
    assert result["classifications"][0]["lob_code"] == "02002"


def test_parse_qwen3_json_with_think_tags():
    """Parse JSON after stripping <think>...</think> block."""
    from src.nodes.rag_classification import parse_qwen3_json

    raw = '<think>Let me reason about this carefully.</think>\n{"classifications": [{"lob_code": "04001", "lob_name": "TELEFONIA IP", "inventory": "Inventario", "explanation": "telefono", "llm_confidence": 85}]}'
    result = parse_qwen3_json(raw)
    assert result["classifications"][0]["lob_code"] == "04001"


def test_parse_qwen3_json_with_markdown_fences():
    """Parse JSON wrapped in markdown code fences."""
    from src.nodes.rag_classification import parse_qwen3_json

    raw = '```json\n{"classifications": [{"lob_code": "02002", "lob_name": "TEST", "inventory": "Inventario", "explanation": "x", "llm_confidence": 70}]}\n```'
    result = parse_qwen3_json(raw)
    assert result["classifications"][0]["lob_code"] == "02002"


def test_parse_qwen3_json_with_think_and_fences():
    """Parse JSON with both think tags and markdown fences."""
    from src.nodes.rag_classification import parse_qwen3_json

    raw = '<think>Reasoning here.</think>\n```json\n{"classifications": [{"lob_code": "01001", "lob_name": "CABLAGGI", "inventory": "Inventario", "explanation": "cavi", "llm_confidence": 60}]}\n```'
    result = parse_qwen3_json(raw)
    assert result["classifications"][0]["lob_code"] == "01001"


def test_parse_qwen3_json_invalid_raises():
    """Invalid JSON raises ValueError."""
    from src.nodes.rag_classification import parse_qwen3_json

    with pytest.raises((ValueError, Exception)):
        parse_qwen3_json("this is not json at all")


def test_infer_inventory_filter_hardware():
    from src.nodes.rag_classification import _infer_inventory_filter

    result = _infer_inventory_filter("Hardware: switch fisico, asset durevole.")
    assert result == "Inventario"


def test_infer_inventory_filter_software():
    from src.nodes.rag_classification import _infer_inventory_filter

    result = _infer_inventory_filter("Software: licenza subscription annuale.")
    assert result == "Non in inventario"


def test_infer_inventory_filter_ambiguous():
    from src.nodes.rag_classification import _infer_inventory_filter

    result = _infer_inventory_filter("prodotto ICT generico")
    assert result is None


MOCK_VALID_LLM_RESPONSE = """{
  "classifications": [
    {"lob_code": "02002", "lob_name": "APPARATI CISCO LAN", "inventory": "Inventario", "explanation": "Switch Cisco.", "llm_confidence": 90},
    {"lob_code": "04001", "lob_name": "TELEFONIA IP", "inventory": "Inventario", "explanation": "Telefonia.", "llm_confidence": 60},
    {"lob_code": "01001", "lob_name": "CABLAGGI", "inventory": "Inventario", "explanation": "Cablaggi.", "llm_confidence": 40}
  ]
}"""


def _make_mock_collections(distances=None):
    if distances is None:
        distances = [[0.1, 0.2, 0.3, 0.4, 0.5]]

    mock_assoc = MagicMock()
    mock_assoc.query.return_value = {
        "metadatas": [[
            {"lob_code_str": "02002", "lob_nome": "APPARATI CISCO LAN", "inventario": "Inventario", "descrizione_articolo": "SWITCH 24P"},
            {"lob_code_str": "04001", "lob_nome": "TELEFONIA IP", "inventario": "Inventario", "descrizione_articolo": "IP PHONE"},
            {"lob_code_str": "01001", "lob_nome": "CABLAGGI", "inventario": "Inventario", "descrizione_articolo": "CABLE"},
        ]],
        "distances": distances,
    }

    mock_lob = MagicMock()
    mock_lob.query.return_value = {
        "metadatas": [[
            {"lob_code": "02002", "name": "APPARATI CISCO LAN"},
            {"lob_code": "04001", "name": "TELEFONIA IP"},
        ]],
        "distances": [[0.1, 0.3]],
    }

    return mock_assoc, mock_lob


def test_rag_classification_node_happy_path():
    """Full node produces 3 ranked suggestions."""
    from src.nodes.rag_classification import rag_classification_node

    state = {
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
        "web_enrichment": "Hardware: switch fisico Cisco.",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }

    mock_assoc, mock_lob = _make_mock_collections(distances=[[0.1, 0.2, 0.3]])

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=MOCK_VALID_LLM_RESPONSE)

    with patch("src.nodes.rag_classification.get_collections", return_value=(mock_lob, mock_assoc)), \
         patch("src.nodes.rag_classification.ChatOllama", return_value=mock_llm), \
         patch("src.nodes.rag_classification._embed_query", return_value=[0.1] * 384):
        result = rag_classification_node(state)

    assert len(result["classification"]) == 3
    assert result["classification"][0]["rank"] == 1
    assert result["classification"][0]["lob_code"] == "02002"
    assert "confidence" in result["classification"][0]
    assert result.get("error") is None


def test_rag_classification_node_llm_failure():
    """When LLM fails twice, returns structured error."""
    from src.nodes.rag_classification import rag_classification_node

    state = {
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

    mock_assoc, mock_lob = _make_mock_collections()
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="not valid json at all")

    with patch("src.nodes.rag_classification.get_collections", return_value=(mock_lob, mock_assoc)), \
         patch("src.nodes.rag_classification.ChatOllama", return_value=mock_llm), \
         patch("src.nodes.rag_classification._embed_query", return_value=[0.1] * 384):
        result = rag_classification_node(state)

    # Should not crash; should set error and return empty or partial classification
    assert result.get("error") is not None or result.get("classification") == []
