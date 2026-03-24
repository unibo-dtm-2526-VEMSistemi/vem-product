import type { DataSource, RagDocumentChunk } from "../types";

export class ProductsSource implements DataSource {
  constructor(private readonly _filePath: string) {}

  async loadChunks(): Promise<RagDocumentChunk[]> {
    // TODO: Parse real product catalog source file.
    return [];
  }
}

