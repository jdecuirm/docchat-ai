import { render, fireEvent, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import DropZone from "./DropZone";

describe("DropZone", () => {
  it("calls onUpload when a valid PDF is dropped", () => {
    const onUpload = vi.fn();
    render(<DropZone onUpload={onUpload} />);
    const zone = screen.getByTestId("drop-zone");
    const file = new File(["content"], "report.pdf", {
      type: "application/pdf",
    });
    fireEvent.drop(zone, {
      dataTransfer: { files: [file], types: ["Files"] },
    });
    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it("calls onUpload when a valid DOCX is dropped", () => {
    const onUpload = vi.fn();
    render(<DropZone onUpload={onUpload} />);
    const zone = screen.getByTestId("drop-zone");
    const file = new File([""], "notes.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    fireEvent.drop(zone, {
      dataTransfer: { files: [file], types: ["Files"] },
    });
    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it("shows error and does not call onUpload for invalid extension", () => {
    const onUpload = vi.fn();
    render(<DropZone onUpload={onUpload} />);
    const zone = screen.getByTestId("drop-zone");
    const file = new File([""], "image.png", { type: "image/png" });
    fireEvent.drop(zone, {
      dataTransfer: { files: [file], types: ["Files"] },
    });
    expect(onUpload).not.toHaveBeenCalled();
    expect(screen.getByText(/only pdf and docx/i)).toBeInTheDocument();
  });

  it("shows error and does not call onUpload when file exceeds 10 MB", () => {
    const onUpload = vi.fn();
    render(<DropZone onUpload={onUpload} />);
    const zone = screen.getByTestId("drop-zone");
    // Create a file with size > 10MB (10 * 1024 * 1024 + 1 bytes)
    const oversized = new File(["x".repeat(1)], "big.pdf", {
      type: "application/pdf",
    });
    Object.defineProperty(oversized, "size", { value: 10 * 1024 * 1024 + 1 });
    fireEvent.drop(zone, {
      dataTransfer: { files: [oversized], types: ["Files"] },
    });
    expect(onUpload).not.toHaveBeenCalled();
    expect(screen.getByText(/10 mb/i)).toBeInTheDocument();
  });
});
