import type { DataSource, RagDocumentChunk } from "../types";

export class ChartOfAccountsSource implements DataSource {
  constructor(private readonly _filePath: string) {}

  async loadChunks(): Promise<RagDocumentChunk[]> {
    // TODO: Parse real chart-of-accounts source file (CSV/JSON/DB export).
    return [];
  }
}

