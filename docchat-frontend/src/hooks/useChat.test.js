import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useChat } from "./useChat";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

function makeStream(chunks) {
  const encoder = new TextEncoder();
  let i = 0;
  return {
    ok: true,
    body: {
      getReader() {
        return {
          async read() {
            if (i >= chunks.length) return { done: true, value: undefined };
            return { done: false, value: encoder.encode(chunks[i++]) };
          },
        };
      },
    },
  };
}

describe("useChat", () => {
  it("appends user and ai messages on sendMessage", async () => {
    mockFetch.mockResolvedValueOnce(makeStream(["data: hi\n\n"]));
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage("hello");
    });
    expect(result.current.messages[0]).toMatchObject({
      role: "user",
      content: "hello",
    });
    expect(result.current.messages[1]).toMatchObject({ role: "ai" });
  });

  it("accumulates tokens in the ai message", async () => {
    mockFetch.mockResolvedValueOnce(
      makeStream(["data: Hello\n\n", "data:  world\n\n"]),
    );
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage("test");
    });
    expect(result.current.messages[1].content).toBe("Hello world");
  });

  it("sets sources when event: citations arrives", async () => {
    const sources = [
      {
        source_filename: "f.pdf",
        page_number: 1,
        relevance_score: 0.91,
        text: "ctx",
        chunk_index: 0,
      },
    ];
    mockFetch.mockResolvedValueOnce(
      makeStream([
        "data: answer\n\n",
        `event: citations\ndata: ${JSON.stringify(sources)}\n\n`,
      ]),
    );
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage("test");
    });
    expect(result.current.messages[1].sources).toEqual(sources);
  });

  it("sets streaming to false after stream ends", async () => {
    mockFetch.mockResolvedValueOnce(makeStream(["data: done\n\n"]));
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage("test");
    });
    expect(result.current.streaming).toBe(false);
  });

  it("sets isError and error content on event: error", async () => {
    mockFetch.mockResolvedValueOnce(
      makeStream([
        'event: error\ndata: {"message":"something went wrong"}\n\n',
      ]),
    );
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage("test");
    });
    expect(result.current.messages[1].isError).toBe(true);
    expect(result.current.messages[1].content).toBe(
      "Error: something went wrong",
    );
  });

  it("handles token in final chunk without trailing newline", async () => {
    const encoder = new TextEncoder();
    const chunks = ["data: Hello\n\n", "data:  world"]; // last chunk has no \n\n; double-space gives " world" payload
    let i = 0;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      body: {
        getReader() {
          return {
            async read() {
              if (i >= chunks.length) return { done: true, value: undefined };
              return { done: false, value: encoder.encode(chunks[i++]) };
            },
          };
        },
      },
    });
    const { result } = renderHook(() => useChat());
    await act(async () => {
      await result.current.sendMessage("test");
    });
    expect(result.current.messages[1].content).toBe("Hello world");
  });
});
