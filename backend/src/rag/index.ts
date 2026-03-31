import { getRagConfig } from "./config";
import { ChartOfAccountsSource } from "./ingestion/chartOfAccountsSource";
import { ProductsSource } from "./ingestion/productsSource";
import { WebEnrichmentSource } from "./ingestion/webEnrichmentSource";
import { LocalLlmClient } from "./llm/localLlmClient";
import { InMemoryRetriever } from "./retrieval/retriever";
import { AccountingAdvisorService } from "./service/accountingAdvisorService";
import type { RagDocumentChunk } from "./types";
import path from "node:path";

export async function createRagModule() {
  const config = getRagConfig();

  const chartSource = new ChartOfAccountsSource(
    path.join(config.dataRoot, "internal", "chart-of-accounts", "accounts.csv")
  );
  const productSource = new ProductsSource(
    path.join(config.dataRoot, "internal", "articles", "products.csv")
  );
  const webSource = new WebEnrichmentSource(
    path.join(config.dataRoot, "external", "web-cache", "web-analysis.jsonl")
  );

  const chunks: RagDocumentChunk[] = [
    ...(await chartSource.loadChunks()),
    ...(await productSource.loadChunks()),
    ...(await webSource.loadChunks()),
  ];

  const retriever = new InMemoryRetriever(chunks);
  const llmClient = new LocalLlmClient(config.modelBaseUrl, config.modelName);

  const advisorService = new AccountingAdvisorService({
    llmClient,
    retriever,
    topK: config.topK,
    minConfidence: config.minConfidence,
  });

  return { advisorService, config };
}

export * from "./types";

