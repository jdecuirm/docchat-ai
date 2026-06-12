import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ChatInput from "./ChatInput";

describe("ChatInput", () => {
  it("send button is disabled when input is empty", () => {
    render(<ChatInput onSend={vi.fn()} streaming={false} />);
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("send button is disabled while streaming", () => {
    render(<ChatInput onSend={vi.fn()} streaming={true} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Hello" } });
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("calls onSend with trimmed value on button click and clears input", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} streaming={false} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "  What is this?  " } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    expect(onSend).toHaveBeenCalledWith("What is this?");
    expect(input.value).toBe("");
  });

  it("calls onSend on Enter key and clears input", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} streaming={false} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "A question" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: false });
    expect(onSend).toHaveBeenCalledWith("A question");
    expect(input.value).toBe("");
  });

  it("does not call onSend on Shift+Enter", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} streaming={false} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Line one" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
    expect(onSend).not.toHaveBeenCalled();
  });
});
