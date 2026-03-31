import { ACCOUNTING_ASSISTANT_SYSTEM_PROMPT, buildUserPrompt } from "../prompts";
import type { LlmClient, RagAnswer, RagDocumentChunk, RagQuery, Retriever } from "../types";

interface AccountingAdvisorServiceDeps {
  llmClient: LlmClient;
  retriever: Retriever;
  topK: number;
  minConfidence: number;
}

const FALLBACK_ANSWER: RagAnswer = {
  decision: {
    accountCode: "UNDETERMINED",
    accountName: "Needs manual review",
    inventoryDecision: "unclear",
  },
  explanation: "Insufficient evidence to provide a reliable accounting classification.",
  confidence: 0,
  citations: [],
  generatedAt: new Date(0).toISOString(),
};

export class AccountingAdvisorService {
  constructor(private readonly deps: AccountingAdvisorServiceDeps) {}

  async advise(query: RagQuery): Promise<RagAnswer> {
    const chunks = await this.deps.retriever.search(query.question, this.deps.topK);

    const raw = await this.deps.llmClient.complete([
      { role: "system", content: ACCOUNTING_ASSISTANT_SYSTEM_PROMPT },
      { role: "user", content: buildUserPrompt(query.question, chunks) },
    ]);

    const parsed = this.parseAnswer(raw, chunks);
    parsed.generatedAt = new Date().toISOString();

    if (parsed.confidence < this.deps.minConfidence) {
      parsed.decision.inventoryDecision = "unclear";
    }

    return parsed;
  }

  private parseAnswer(raw: string, chunks: RagDocumentChunk[]): RagAnswer {
    try {
      const json = JSON.parse(raw) as Partial<RagAnswer>;
      const answer: RagAnswer = {
        decision: {
          accountCode: json.decision?.accountCode ?? FALLBACK_ANSWER.decision.accountCode,
          accountName: json.decision?.accountName ?? FALLBACK_ANSWER.decision.accountName,
          inventoryDecision:
            json.decision?.inventoryDecision ?? FALLBACK_ANSWER.decision.inventoryDecision,
        },
        explanation: json.explanation ?? FALLBACK_ANSWER.explanation,
        confidence: Number.isFinite(json.confidence) ? Number(json.confidence) : 0,
        citations: chunks.map((chunk) => ({
          sourceType: chunk.sourceType,
          sourceId: chunk.id,
          title: chunk.metadata?.title,
        })),
        generatedAt: new Date().toISOString(),
      };

      return answer;
    } catch {
      return {
        ...FALLBACK_ANSWER,
        citations: chunks.map((chunk) => ({
          sourceType: chunk.sourceType,
          sourceId: chunk.id,
          title: chunk.metadata?.title,
        })),
        generatedAt: new Date().toISOString(),
      };
    }
  }
}

