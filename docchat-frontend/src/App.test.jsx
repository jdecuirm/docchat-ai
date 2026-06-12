import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App";

vi.mock("./hooks/useDocuments", () => ({
  useDocuments: () => ({
    documents: [],
    uploading: false,
    error: null,
    upload: vi.fn(),
    remove: vi.fn(),
  }),
}));

vi.mock("./hooks/useChat", () => ({
  useChat: () => ({
    messages: [],
    streaming: false,
    sendMessage: vi.fn(),
  }),
}));

describe("App", () => {
  it("renders the header title", () => {
    render(<App />);
    expect(screen.getByText(/docchat/i)).toBeInTheDocument();
  });

  it("renders the sidebar and chat panel", () => {
    render(<App />);
    expect(screen.getByTestId("drop-zone")).toBeInTheDocument();
    expect(
      screen.getByRole("textbox", { name: /chat input/i }),
    ).toBeInTheDocument();
  });
});
