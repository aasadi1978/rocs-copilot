import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";

import { useChatStream } from "../useChatStream";

function mockSSEResponse(eventLines: string[]): Response {
  const body = eventLines.join("\n") + "\n";
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "Content-Type": "text/event-stream" },
  });
}

describe("useChatStream", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("parses token events into a streaming answer", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      mockSSEResponse([
        "event: token",
        'data: {"text": "Hello "}',
        "",
        "event: token",
        'data: {"text": "world."}',
        "",
        "event: done",
        "data: {}",
      ])
    );

    const { result } = renderHook(() => useChatStream());

    await act(async () => {
      await result.current.send("hi", []);
    });

    await waitFor(() => {
      expect(result.current.answer).toBe("Hello world.");
      expect(result.current.streaming).toBe(false);
    });
  });

  it("captures source chunks after done", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      mockSSEResponse([
        "event: token",
        'data: {"text": "Answer."}',
        "",
        "event: source",
        'data: {"chunks": [{"id":"m.pdf:p1","filename":"m.pdf","page":1,"score":0.8,"snippet":"..."}]}',
        "",
        "event: done",
        "data: {}",
      ])
    );

    const { result } = renderHook(() => useChatStream());

    await act(async () => {
      await result.current.send("q", []);
    });

    await waitFor(() => {
      expect(result.current.sources).toHaveLength(1);
      expect(result.current.sources[0].filename).toBe("m.pdf");
    });
  });

  it("captures error events with retryable flag", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      mockSSEResponse([
        "event: error",
        'data: {"code":"llm_unavailable","message":"down","retryable":true}',
        "",
        "event: done",
        "data: {}",
      ])
    );

    const { result } = renderHook(() => useChatStream());

    await act(async () => {
      await result.current.send("q", []);
    });

    await waitFor(() => {
      expect(result.current.error).toEqual({
        code: "llm_unavailable",
        message: "down",
        retryable: true,
      });
    });
  });

  it("supports abort via the returned controller", async () => {
    const neverResolves = new Promise<Response>(() => {});
    vi.spyOn(global, "fetch").mockReturnValue(neverResolves as Promise<Response>);

    const { result } = renderHook(() => useChatStream());

    act(() => {
      void result.current.send("q", []);
    });

    expect(result.current.streaming).toBe(true);

    act(() => {
      result.current.abort();
    });

    await waitFor(() => {
      expect(result.current.streaming).toBe(false);
    });
  });
});
