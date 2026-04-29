from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import OLLAMA_MODEL
from src.data_loader import load_datasets, get_train_test_split, get_lob_codes
from src.vectorstore_setup import initialize_vectorstore
from src.graph import classify_article


@asynccontextmanager
async def lifespan(app: FastAPI):
    lob_df, _ = load_datasets()
    train_df, _ = get_train_test_split()
    initialize_vectorstore(train_df, lob_df)
    yield


app = FastAPI(
    title="VEM AI Classification Agent",
    description="AI-powered accounting classification for ICT products",
    version="0.1.0",
    lifespan=lifespan,
)


class ClassificationRequest(BaseModel):
    article_code: str


class LOBSuggestion(BaseModel):
    rank: int
    lob_code: str
    lob_name: str
    inventory: str
    explanation: str
    confidence: float


class ClassificationResponse(BaseModel):
    article_code: str
    article_description: str | None
    existing_lob: str | None
    existing_inventory: str | None
    web_enrichment: str | None
    suggestions: list[LOBSuggestion]
    error: str | None


@app.post("/classify", response_model=ClassificationResponse)
async def classify(request: ClassificationRequest) -> ClassificationResponse:
    result = classify_article(request.article_code)
    if result.get("error") and not result.get("suggestions"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "model": OLLAMA_MODEL}


@app.get("/lob-codes")
async def list_lob_codes() -> list[dict]:
    """Return the full LOB taxonomy for reference."""
    lob_df = get_lob_codes()
    return lob_df.to_dict(orient="records")
