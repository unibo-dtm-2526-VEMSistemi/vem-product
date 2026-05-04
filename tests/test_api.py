from unittest.mock import patch
from fastapi.testclient import TestClient


MOCK_CLASSIFY_FOUND = {
    "article_code": "ART-001",
    "article_description": "CISCO SWITCH 24P",
    "existing_lob": "02002 - APPARATI CISCO LAN",
    "existing_inventory": "Inventario",
    "web_enrichment": "Hardware: switch Cisco.",
    "suggestions": [
        {
            "rank": 1,
            "lob_code": "02002",
            "lob_name": "APPARATI CISCO LAN",
            "inventory": "Inventario",
            "explanation": "Switch Cisco.",
            "confidence": 0.88,
        },
        {
            "rank": 2,
            "lob_code": "04001",
            "lob_name": "TELEFONIA IP",
            "inventory": "Inventario",
            "explanation": "Telefonia.",
            "confidence": 0.55,
        },
        {
            "rank": 3,
            "lob_code": "01001",
            "lob_name": "CABLAGGI",
            "inventory": "Inventario",
            "explanation": "Cablaggi.",
            "confidence": 0.30,
        },
    ],
    "error": None,
}

MOCK_CLASSIFY_NOT_FOUND = {
    "article_code": "NOPE",
    "article_description": None,
    "existing_lob": None,
    "existing_inventory": None,
    "web_enrichment": None,
    "suggestions": [],
    "error": "Article not found in dataset: NOPE",
}


def _get_test_client():
    """Import app inside function to allow patching startup."""
    from src.api import app

    return TestClient(app)


def test_health_endpoint():
    client = _get_test_client()
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model" in body


def test_classify_found():
    with (
        patch("src.api.classify_article", return_value=MOCK_CLASSIFY_FOUND),
        patch("src.api.load_datasets", return_value=(None, None)),
        patch("src.api.get_train_test_split", return_value=(None, None)),
        patch("src.api.initialize_vectorstore"),
    ):
        client = _get_test_client()
        response = client.post("/classify", json={"article_code": "ART-001"})

    assert response.status_code == 200
    body = response.json()
    assert body["article_code"] == "ART-001"
    assert body["article_description"] == "CISCO SWITCH 24P"
    assert len(body["suggestions"]) == 3
    assert body["suggestions"][0]["confidence"] == 0.88
    assert body["error"] is None


def test_classify_not_found():
    with (
        patch("src.api.classify_article", return_value=MOCK_CLASSIFY_NOT_FOUND),
        patch("src.api.load_datasets", return_value=(None, None)),
        patch("src.api.get_train_test_split", return_value=(None, None)),
        patch("src.api.initialize_vectorstore"),
    ):
        client = _get_test_client()
        response = client.post("/classify", json={"article_code": "NOPE"})

    assert response.status_code == 404


def test_lob_codes_endpoint():
    import pandas as pd
    import io

    lob_csv = "LOB Code,Name\n01001,CABLAGGI COMMSCOPE\n02002,APPARATI CISCO LAN\n"
    mock_lob_df = pd.read_csv(io.StringIO(lob_csv), dtype=str)

    with (
        patch("src.api.get_lob_codes", return_value=mock_lob_df),
        patch("src.api.load_datasets", return_value=(None, None)),
        patch("src.api.get_train_test_split", return_value=(None, None)),
        patch("src.api.initialize_vectorstore"),
    ):
        client = _get_test_client()
        response = client.get("/lob-codes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["LOB Code"] == "01001"


def test_classify_missing_article_code():
    client = _get_test_client()
    response = client.post("/classify", json={})
    assert response.status_code == 422  # Pydantic validation error
