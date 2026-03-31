import path from "node:path";

export interface RagConfig {
  modelBaseUrl: string;
  modelName: string;
  topK: number;
  minConfidence: number;
  dataRoot: string;
}

function parseNumber(value: string | undefined, fallback: number): number {
  if (!value) return fallback;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function getRagConfig(): RagConfig {
  return {
    modelBaseUrl: process.env.RAG_LLM_BASE_URL ?? "http://localhost:11434",
    modelName: process.env.RAG_LLM_MODEL ?? "llama3.1:8b",
    topK: parseNumber(process.env.RAG_RETRIEVAL_TOP_K, 5),
    minConfidence: parseNumber(process.env.RAG_MIN_CONFIDENCE, 0.55),
    dataRoot: path.resolve(process.cwd(), "backend", "data"),
  };
}

