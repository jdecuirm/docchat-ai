import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import SourcesAccordion from "./SourcesAccordion";

const SOURCES = [
  { source_filename: "report.pdf", page_number: 3, relevance_score: 0.91 },
  { source_filename: "notes.docx", page_number: 1, relevance_score: 0.78 },
];

describe("SourcesAccordion", () => {
  it("renders collapsed by default", () => {
    render(<SourcesAccordion sources={SOURCES} />);
    expect(screen.getByText(/sources \(2\)/i)).toBeInTheDocument();
    expect(screen.queryByText("report.pdf")).not.toBeInTheDocument();
  });

  it("expands when header is clicked", () => {
    render(<SourcesAccordion sources={SOURCES} />);
    fireEvent.click(screen.getByRole("button", { name: /sources/i }));
    expect(screen.getByText(/report\.pdf/)).toBeInTheDocument();
    expect(screen.getByText(/notes\.docx/)).toBeInTheDocument();
  });

  it("collapses again on second click", () => {
    render(<SourcesAccordion sources={SOURCES} />);
    const btn = screen.getByRole("button", { name: /sources/i });
    fireEvent.click(btn);
    fireEvent.click(btn);
    expect(screen.queryByText("report.pdf")).not.toBeInTheDocument();
  });

  it("renders nothing when sources array is empty", () => {
    const { container } = render(<SourcesAccordion sources={[]} />);
    expect(container.firstChild).toBeNull();
  });
});
