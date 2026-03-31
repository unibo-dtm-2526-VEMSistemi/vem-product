from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

SERVICE_KEYWORDS = ("service", "subscription", "saas")
HARDWARE_KEYWORDS = ("switch", "hardware", "device")


class RagQuery(BaseModel):
    question: str = Field(min_length=3)
    language: Literal["en", "it"] = "en"
    sessionId: str | None = None


class RagDecision(BaseModel):
    accountCode: str
    accountName: str
    inventoryDecision: Literal["inventory", "non_inventory", "unclear"]


class SourceReference(BaseModel):
    sourceType: Literal["chart_of_accounts", "product_catalog", "web_enrichment"]
    sourceId: str
    title: str | None = None
    score: float | None = None


class RagAnswer(BaseModel):
    decision: RagDecision
    explanation: str
    confidence: float
    citations: list[SourceReference]
    generatedAt: str


app = FastAPI(title="VEM Product RAG Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "message": "VEM backend is running"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "healthy"}


def _contains_any(question: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in question for keyword in keywords)


def _classify_question(question: str) -> tuple[RagDecision, str, float]:
    if _contains_any(question, SERVICE_KEYWORDS):
        return (
            RagDecision(
                accountCode="SERV-001",
                accountName="ICT Service Costs",
                inventoryDecision="non_inventory",
            ),
            (
                "The query indicates a recurring or service-based ICT item; "
                "it is usually classified as operating service expense."
            ),
            0.58,
        )

    if _contains_any(question, HARDWARE_KEYWORDS):
        return (
            RagDecision(
                accountCode="HW-001",
                accountName="ICT Hardware Inventory",
                inventoryDecision="inventory",
            ),
            (
                "The query looks like a physical ICT product; "
                "inventory treatment is likely until sold or allocated."
            ),
            0.62,
        )

    return (
        RagDecision(
            accountCode="UNDETERMINED",
            accountName="Needs manual review",
            inventoryDecision="unclear",
        ),
        (
            "No reliable evidence yet. Real internal data sources are not connected, "
            "so this answer stays consultative and low confidence."
        ),
        0.35,
    )


def _default_citations() -> list[SourceReference]:
    return [
        SourceReference(sourceType="chart_of_accounts", sourceId="placeholder-coa"),
        SourceReference(sourceType="product_catalog", sourceId="placeholder-products"),
    ]


@app.post("/api/rag/advise", response_model=RagAnswer)
def rag_advise(payload: RagQuery) -> RagAnswer:
    question = payload.question.lower()
    decision, explanation, confidence = _classify_question(question)

    return RagAnswer(
        decision=decision,
        explanation=explanation,
        confidence=confidence,
        citations=_default_citations(),
        generatedAt=datetime.now(timezone.utc).isoformat(),
    )
