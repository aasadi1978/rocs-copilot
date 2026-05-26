import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import { SourcePanel } from "../SourcePanel";
import type { SourceChunk } from "../../types/api";

const chunks: SourceChunk[] = [
  { id: "m.pdf:p1", filename: "manual.pdf", page: 1, score: 0.82, snippet: "Routing details" },
  { id: "m.pdf:p3", filename: "errata.pdf", page: 3, score: 0.71, snippet: "Error codes" },
];

describe("SourcePanel", () => {
  it("renders nothing when chunks is empty", () => {
    const { container } = render(<SourcePanel chunks={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders a summary count when collapsed", () => {
    render(<SourcePanel chunks={chunks} />);
    expect(screen.getByText(/2 sources/i)).toBeInTheDocument();
  });

  it("expands to show filenames, pages, and scores on click", () => {
    render(<SourcePanel chunks={chunks} />);
    fireEvent.click(screen.getByRole("button", { name: /sources/i }));
    expect(screen.getByText(/manual\.pdf/i)).toBeInTheDocument();
    expect(screen.getByText(/p\.1/i)).toBeInTheDocument();
    expect(screen.getByText(/0\.82/)).toBeInTheDocument();
  });
});
