import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { Chat } from "../Chat";
import * as hookModule from "../../hooks/useChatStream";

function mockHook(overrides: Partial<ReturnType<typeof hookModule.useChatStream>>) {
  const send = vi.fn();
  const abort = vi.fn();
  const reset = vi.fn();
  vi.spyOn(hookModule, "useChatStream").mockReturnValue({
    answer: "",
    sources: [],
    error: null,
    streaming: false,
    send,
    abort,
    reset,
    ...overrides,
  });
  return { send, abort, reset };
}

describe("Chat", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("submits a question and renders the user bubble", async () => {
    const { send } = mockHook({});
    render(<Chat />);
    const input = screen.getByPlaceholderText(/ask about ROCS/i);
    fireEvent.change(input, { target: { value: "What is SAMPLE-001?" } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => {
      expect(send).toHaveBeenCalledWith("What is SAMPLE-001?", []);
      expect(screen.getByText("What is SAMPLE-001?")).toBeInTheDocument();
    });
  });

  it("renders an error bubble with retry on llm_unavailable", async () => {
    const { send } = mockHook({
      error: { code: "llm_unavailable", message: "down", retryable: true },
      streaming: false,
    });
    render(<Chat />);
    fireEvent.change(screen.getByPlaceholderText(/ask about ROCS/i), {
      target: { value: "hi" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => {
      expect(screen.getByText(/down/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /retry/i }));
    expect(send).toHaveBeenCalledTimes(2);
  });
});
