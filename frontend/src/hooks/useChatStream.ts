import { useCallback, useRef, useState } from "react";
import type {
  ChatStreamEvent,
  ChatTurn,
  SourceChunk,
} from "../types/api";

interface UseChatStream {
  answer: string;
  sources: SourceChunk[];
  error: { code: string; message: string; retryable: boolean } | null;
  streaming: boolean;
  send: (question: string, history: ChatTurn[]) => Promise<void>;
  abort: () => void;
  reset: () => void;
}

export function useChatStream(): UseChatStream {
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<SourceChunk[]>([]);
  const [error, setError] = useState<UseChatStream["error"]>(null);
  const [streaming, setStreaming] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    setAnswer("");
    setSources([]);
    setError(null);
  }, []);

  const abort = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setStreaming(false);
  }, []);

  const send = useCallback(
    async (question: string, history: ChatTurn[]) => {
      reset();
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setStreaming(true);

      try {
        const resp = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, history }),
          signal: controller.signal,
        });
        if (!resp.ok || !resp.body) {
          setError({
            code: "internal",
            message: `Request failed: ${resp.status}`,
            retryable: true,
          });
          return;
        }
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let idx;
          while ((idx = buffer.indexOf("\n\n")) !== -1) {
            const raw = buffer.slice(0, idx);
            buffer = buffer.slice(idx + 2);
            const evt = parseEvent(raw);
            if (evt) applyEvent(evt);
          }
        }
        if (buffer.trim()) {
          const evt = parseEvent(buffer);
          if (evt) applyEvent(evt);
        }
      } catch (e) {
        if ((e as Error).name === "AbortError") {
          // user cancelled — silent
        } else {
          setError({
            code: "internal",
            message: (e as Error).message,
            retryable: true,
          });
        }
      } finally {
        setStreaming(false);
        controllerRef.current = null;
      }

      function applyEvent(evt: ChatStreamEvent) {
        switch (evt.kind) {
          case "token":
            setAnswer((prev) => prev + evt.text);
            break;
          case "source":
            setSources(evt.chunks);
            break;
          case "error":
            setError({
              code: evt.code,
              message: evt.message,
              retryable: evt.retryable,
            });
            break;
          case "done":
            break;
        }
      }
    },
    [reset]
  );

  return { answer, sources, error, streaming, send, abort, reset };
}

function parseEvent(raw: string): ChatStreamEvent | null {
  let eventName = "";
  let dataLine = "";
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) eventName = line.slice("event:".length).trim();
    else if (line.startsWith("data:")) dataLine += line.slice("data:".length).trim();
  }
  if (!eventName || !dataLine) return null;
  try {
    const payload = JSON.parse(dataLine);
    switch (eventName) {
      case "token":
        return { kind: "token", text: payload.text };
      case "source":
        return { kind: "source", chunks: payload.chunks };
      case "done":
        return { kind: "done" };
      case "error":
        return {
          kind: "error",
          code: payload.code,
          message: payload.message,
          retryable: payload.retryable,
        };
      default:
        return null;
    }
  } catch {
    return null;
  }
}
