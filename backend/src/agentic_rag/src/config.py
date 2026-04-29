from pathlib import Path
from dotenv import load_dotenv

# Paths — resolved relative to this file so the module is portable
_MODULE_ROOT = Path(__file__).parent.parent  # backend/src/agentic_rag/

load_dotenv(_MODULE_ROOT / ".env")

DATA_DIR = _MODULE_ROOT / "data"
LOB_CODES_PATH = DATA_DIR / "lob_codes.csv"
ARTICLES_PATH = DATA_DIR / "rag_input_dataset.csv"
CHROMA_PERSIST_DIR = str(_MODULE_ROOT / "vectorstore")

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:8b"
OLLAMA_TEMPERATURE = 0.1
OLLAMA_NUM_CTX = 4096    # 3 JSON suggestions fit well under 512 output tokens
# Speed tip: set OLLAMA_FLASH_ATTENTION=1 and OLLAMA_KV_CACHE_TYPE=q8_0 in env

# ChromaDB collections
CHROMA_COLLECTION_LOB = "lob_codes"
CHROMA_COLLECTION_ASSOCIATIONS = "article_associations"

# Retrieval
TOP_K_ASSOCIATIONS = 15
TOP_K_LOB = 10
FINAL_TOP_N = 3

# Train/test split
TEST_SPLIT_RATIO = 0.15
RANDOM_SEED = 42

# Tavily
TAVILY_MAX_RESULTS = 3

# API
API_HOST = "0.0.0.0"
API_PORT = 8000

# Embedding model
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
