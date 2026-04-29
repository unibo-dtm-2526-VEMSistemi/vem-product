from typing import TypedDict


class AgentState(TypedDict):
    article_code: str
    article_info: dict | None
    web_enrichment: str
    retrieval_results: list[dict]
    classification: list[dict]
    error: str | None
