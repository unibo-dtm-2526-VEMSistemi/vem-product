from src.state import AgentState


def test_agent_state_keys():
    state: AgentState = {
        "article_code": "ART-001",
        "article_info": None,
        "web_enrichment": "",
        "retrieval_results": [],
        "classification": [],
        "error": None,
    }
    assert state["article_code"] == "ART-001"
    assert state["article_info"] is None
    assert state["web_enrichment"] == ""
    assert state["retrieval_results"] == []
    assert state["classification"] == []
    assert state["error"] is None


def test_agent_state_with_data():
    state: AgentState = {
        "article_code": "ART-001",
        "article_info": {"codice_articolo": "ART-001", "lob_code_str": "02002"},
        "web_enrichment": "Hardware switch device.",
        "retrieval_results": [{"lob_code": "02002", "score": 0.95}],
        "classification": [{"lob_code": "02002", "confidence": 0.9}],
        "error": None,
    }
    assert state["article_info"]["lob_code_str"] == "02002"
    assert len(state["retrieval_results"]) == 1
    assert state["classification"][0]["confidence"] == 0.9
