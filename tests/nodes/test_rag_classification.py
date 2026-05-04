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
        "metadatas": [
            [
                {
                    "lob_code_str": "02002",
                    "lob_nome": "APPARATI CISCO LAN",
                    "inventario": "Inventario",
                    "descrizione_articolo": "SWITCH 24P",
                },
                {
                    "lob_code_str": "04001",
                    "lob_nome": "TELEFONIA IP",
                    "inventario": "Inventario",
                    "descrizione_articolo": "IP PHONE",
                },
                {
                    "lob_code_str": "01001",
                    "lob_nome": "CABLAGGI",
                    "inventario": "Inventario",
                    "descrizione_articolo": "CABLE",
                },
            ]
        ],
        "distances": distances,
    }

    mock_lob = MagicMock()
    mock_lob.query.return_value = {
        "metadatas": [
            [
                {"lob_code": "02002", "name": "APPARATI CISCO LAN"},
                {"lob_code": "04001", "name": "TELEFONIA IP"},
            ]
        ],
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

    with (
        patch(
            "src.nodes.rag_classification.get_collections",
            return_value=(mock_lob, mock_assoc),
        ),
        patch("src.nodes.rag_classification.ChatOllama", return_value=mock_llm),
        patch("src.nodes.rag_classification._embed_query", return_value=[0.1] * 384),
    ):
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

    with (
        patch(
            "src.nodes.rag_classification.get_collections",
            return_value=(mock_lob, mock_assoc),
        ),
        patch("src.nodes.rag_classification.ChatOllama", return_value=mock_llm),
        patch("src.nodes.rag_classification._embed_query", return_value=[0.1] * 384),
    ):
        result = rag_classification_node(state)

    # Should not crash; should set error and return empty or partial classification
    assert result.get("error") is not None or result.get("classification") == []


def test_embed_query_calls_embedding_function():
    """_embed_query returns the first embedding vector for the query."""
    from src.nodes.rag_classification import _embed_query

    mock_ef = MagicMock(return_value=[[0.1, 0.2, 0.3]])

    with patch(
        "src.nodes.rag_classification._get_embedding_function", return_value=mock_ef
    ):
        result = _embed_query("CISCO SWITCH 24P")

    mock_ef.assert_called_once_with(["CISCO SWITCH 24P"])
    assert result == [0.1, 0.2, 0.3]


def test_rag_classification_ignores_web_enrichment():
    """rag_classification must not use web_enrichment content in LLM messages."""
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
        "web_enrichment": "QUESTO_TESTO_NON_DEVE_APPARIRE_NEI_MESSAGGI_LLM",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }

    mock_assoc, mock_lob = _make_mock_collections(distances=[[0.1, 0.2, 0.3]])

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"classifications": [{"lob_code": "02002", "lob_name": "APPARATI CISCO LAN", "inventory": "Inventario", "explanation": "Test.", "llm_confidence": 80}, {"lob_code": "04001", "lob_name": "TELEFONIA IP", "inventory": "Inventario", "explanation": "Test.", "llm_confidence": 60}, {"lob_code": "01001", "lob_name": "CABLAGGI", "inventory": "Inventario", "explanation": "Test.", "llm_confidence": 40}]}'
    )

    with (
        patch(
            "src.nodes.rag_classification.get_collections",
            return_value=(mock_lob, mock_assoc),
        ),
        patch("src.nodes.rag_classification.ChatOllama", return_value=mock_llm),
        patch("src.nodes.rag_classification._embed_query", return_value=[0.1] * 10),
        patch("src.nodes.rag_classification.compute_confidence", return_value=75),
    ):
        rag_classification_node(state)

    # Get all message content strings passed to LLM
    call_args = mock_llm.invoke.call_args
    messages = call_args[0][0]  # first positional arg is the messages list
    all_content = " ".join(m.content for m in messages)
    assert "QUESTO_TESTO_NON_DEVE_APPARIRE" not in all_content
