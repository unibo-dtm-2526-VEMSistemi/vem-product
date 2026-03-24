import type { RagDocumentChunk, Retriever } from "../types";

export class InMemoryRetriever implements Retriever {
  constructor(private readonly chunks: RagDocumentChunk[]) {}

  async search(query: string, topK: number): Promise<RagDocumentChunk[]> {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return [];

    const ranked = this.chunks
      .map((chunk) => {
        const haystack = `${chunk.content} ${JSON.stringify(chunk.metadata ?? {})}`.toLowerCase();
        const score = haystack.includes(normalized) ? 1 : 0;
        return { chunk, score };
      })
      .filter((row) => row.score > 0)
      .slice(0, topK)
      .map((row) => row.chunk);

    return ranked;
  }
}

