import type { RagDocumentChunk } from "./types";

export const ACCOUNTING_ASSISTANT_SYSTEM_PROMPT = `
You are a VEM accounting advisory assistant for ICT products and services.
You must answer in a consultative way and never trigger ERP or accounting actions.
You must output valid JSON with this shape:
{
  "decision": {
    "accountCode": "string",
    "accountName": "string",
    "inventoryDecision": "inventory | non_inventory | unclear"
  },
  "explanation": "string",
  "confidence": number
}
Rules:
- Use only the provided context and query.
- If evidence is weak, reduce confidence and set inventoryDecision to "unclear".
- Keep explanation concise and operational.
`.trim();

export function buildUserPrompt(question: string, chunks: RagDocumentChunk[]): string {
  const context = chunks
    .map((chunk, index) => {
      const label = `CTX_${index + 1}`;
      return `[${label}] ${chunk.content}`;
    })
    .join("\n\n");

  return [
    `User question: ${question}`,
    "",
    "Context:",
    context || "No context provided.",
    "",
    "Return JSON only.",
  ].join("\n");
}

