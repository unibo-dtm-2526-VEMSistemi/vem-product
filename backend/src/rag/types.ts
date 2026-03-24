export type SourceType = "chart_of_accounts" | "product_catalog" | "web_enrichment";

export type InventoryDecision = "inventory" | "non_inventory" | "unclear";

export interface SourceReference {
  sourceType: SourceType;
  sourceId: string;
  title?: string;
  score?: number;
}

export interface RagDocumentChunk {
  id: string;
  sourceType: SourceType;
  content: string;
  metadata?: Record<string, string>;
}

export interface RagQuery {
  question: string;
  language?: "en" | "it";
  sessionId?: string;
}

export interface RagDecision {
  accountCode: string;
  accountName: string;
  inventoryDecision: InventoryDecision;
}

export interface RagAnswer {
  decision: RagDecision;
  explanation: string;
  confidence: number;
  citations: SourceReference[];
  generatedAt: string;
}

export interface LlmChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface LlmClient {
  complete(messages: LlmChatMessage[]): Promise<string>;
}

export interface Retriever {
  search(query: string, topK: number): Promise<RagDocumentChunk[]>;
}

export interface DataSource {
  loadChunks(): Promise<RagDocumentChunk[]>;
}

