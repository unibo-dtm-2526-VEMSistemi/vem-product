from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def _run_server() -> None:
    import uvicorn
    from config import API_HOST, API_PORT

    uvicorn.run("src.api:app", host=API_HOST, port=API_PORT, reload=True)


def _run_cli(article_code: str) -> None:
    from config import CHROMA_PERSIST_DIR
    from vectorstore_setup import initialize_vectorstore
    from data_loader import load_datasets, get_train_test_split
    from graph import classify_article

    print(f"Loading datasets...")
    lob_df, _ = load_datasets()
    train_df, _ = get_train_test_split()

    print(f"Initializing vectorstore at {CHROMA_PERSIST_DIR}...")
    initialize_vectorstore(train_df, lob_df)

    print(f"Classifying article: {article_code}")
    result = classify_article(article_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        _run_server()
    else:
        code = sys.argv[1] if len(sys.argv) > 1 else input("Enter article code: ").strip()
        _run_cli(code)
