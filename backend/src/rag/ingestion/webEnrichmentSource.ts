import type { DataSource, RagDocumentChunk } from "../types";

export class WebEnrichmentSource implements DataSource {
  constructor(private readonly _cachePath: string) {}

  async loadChunks(): Promise<RagDocumentChunk[]> {
    // TODO: Load normalized external web analysis cache.
    return [];
  }
}

