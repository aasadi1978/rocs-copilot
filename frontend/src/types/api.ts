/** Mirrors backend SSE contract from spec §7.2 + §8.2. */

export interface ChatRequest {
  question: string;
  history: ChatTurn[];
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface SourceChunk {
  id: string;
  filename: string;
  page: number;
  score: number;
  snippet: string;
}

export type ChatStreamEvent =
  | { kind: "token"; text: string }
  | { kind: "source"; chunks: SourceChunk[] }
  | { kind: "done" }
  | {
      kind: "error";
      code: "no_corpus" | "llm_unavailable" | "internal";
      message: string;
      retryable: boolean;
    };
