from __future__ import annotations

from src.data_loader import get_article_info, load_datasets
from src.state import AgentState


def db_lookup_node(state: AgentState) -> dict:
    """Node 1: Look up the article in the training dataset."""
    article_code = state["article_code"]

    _, articles_df = load_datasets()
    article_info = get_article_info(article_code, articles_df)

    if article_info is None:
        return {
            "article_info": None,
            "error": f"Article not found in dataset: {article_code}",
        }

    return {
        "article_info": article_info,
        "error": None,
    }
