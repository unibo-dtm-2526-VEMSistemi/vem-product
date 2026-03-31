import type { LlmChatMessage, LlmClient } from "../types";

interface OllamaLikeResponse {
  message?: {
    content?: string;
  };
}

export class LocalLlmClient implements LlmClient {
  constructor(
    private readonly baseUrl: string,
    private readonly modelName: string
  ) {}

  async complete(messages: LlmChatMessage[]): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: this.modelName,
        stream: false,
        messages,
      }),
    });

    if (!response.ok) {
      throw new Error(`Local LLM request failed: ${response.status} ${response.statusText}`);
    }

    const payload = (await response.json()) as OllamaLikeResponse;
    return payload.message?.content ?? "";
  }
}

