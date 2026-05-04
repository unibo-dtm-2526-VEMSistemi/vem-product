from unittest.mock import patch
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_root_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_healthz_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert "model" in response.json()


def test_rag_advise_contract() -> None:
    mock_result = {
        "article_code": "ART-001",
        "article_description": "CISCO SWITCH 24P",
        "existing_lob": "02002 - APPARATI CISCO LAN",
        "existing_inventory": "Inventario",
        "web_enrichment": "Hardware switch.",
        "suggestions": [
            {
                "rank": 1,
                "lob_code": "02002",
                "lob_name": "APPARATI CISCO LAN",
                "inventory": "Inventario",
                "explanation": "Switch Cisco.",
                "confidence": 0.88,
            }
        ],
        "error": None,
    }

    with (
        patch("src.api.classify_article", return_value=mock_result),
        patch("src.api.load_datasets", return_value=(None, None)),
        patch("src.api.get_train_test_split", return_value=(None, None)),
        patch("src.api.initialize_vectorstore"),
    ):
        patched_client = TestClient(app)
        response = patched_client.post("/classify", json={"article_code": "ART-001"})

    assert response.status_code == 200
    body = response.json()
    assert body["article_code"] == "ART-001"
    assert len(body["suggestions"]) >= 1
    assert body["error"] is None
