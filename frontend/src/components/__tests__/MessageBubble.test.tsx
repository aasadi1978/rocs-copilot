import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import { MessageBubble } from "../MessageBubble";

describe("MessageBubble", () => {
  it("renders user variant", () => {
    render(<MessageBubble variant="user" content="What is SAMPLE-001?" />);
    expect(screen.getByText("What is SAMPLE-001?")).toBeInTheDocument();
  });

  it("renders markdown in assistant variant", () => {
    render(<MessageBubble variant="assistant" content="**Bold** and `code`." />);
    expect(screen.getByText("Bold").tagName).toBe("STRONG");
    expect(screen.getByText("code").tagName).toBe("CODE");
  });

  it("renders an error variant with retry button when retryable", () => {
    const onRetry = vi.fn();
    render(
      <MessageBubble
        variant="error"
        content="The assistant is temporarily unavailable."
        retryable
        onRetry={onRetry}
      />
    );
    const btn = screen.getByRole("button", { name: /retry/i });
    fireEvent.click(btn);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("hides retry button when not retryable", () => {
    render(
      <MessageBubble
        variant="error"
        content="No documents indexed yet."
        retryable={false}
      />
    );
    expect(screen.queryByRole("button", { name: /retry/i })).toBeNull();
  });
});
