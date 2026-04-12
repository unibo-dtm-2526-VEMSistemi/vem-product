from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_ok() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_healthz_ok() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_rag_advise_contract() -> None:
    response = client.post(
        "/api/rag/advise",
        json={"question": "SaaS subscription for cybersecurity platform"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "decision" in body
    assert "accountCode" in body["decision"]
    assert "inventoryDecision" in body["decision"]
    assert "confidence" in body
    assert "citations" in body
