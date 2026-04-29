from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    CHROMA_COLLECTION_LOB,
    CHROMA_COLLECTION_ASSOCIATIONS,
    TOP_K_ASSOCIATIONS,
    TOP_K_LOB,
    FINAL_TOP_N,
    TEST_SPLIT_RATIO,
    RANDOM_SEED,
    EMBEDDING_MODEL,
    API_PORT,
)


def test_ollama_defaults():
    assert OLLAMA_BASE_URL == "http://localhost:11434"
    assert OLLAMA_MODEL == "qwen3:8b"


def test_collection_names():
    assert CHROMA_COLLECTION_LOB == "lob_codes"
    assert CHROMA_COLLECTION_ASSOCIATIONS == "article_associations"


def test_retrieval_params():
    assert TOP_K_ASSOCIATIONS == 15
    assert TOP_K_LOB == 10
    assert FINAL_TOP_N == 3


def test_split_params():
    assert 0 < TEST_SPLIT_RATIO < 1
    assert isinstance(RANDOM_SEED, int)


def test_api_port():
    assert API_PORT == 8000
