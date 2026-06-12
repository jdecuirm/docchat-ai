import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useDocuments } from "./useDocuments";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
  mockFetch.mockResolvedValue({
    ok: true,
    json: async () => ({ documents: [] }),
  });
});

describe("useDocuments", () => {
  it("fetches document list on mount", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: ["report.pdf"] }),
    });
    const { result } = renderHook(() => useDocuments());
    await act(async () => {});
    expect(result.current.documents).toEqual(["report.pdf"]);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/documents\/$/),
    );
  });

  it("sets uploading true then false during upload", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ documents: [] }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ documents: ["f.pdf"] }),
      });

    const { result } = renderHook(() => useDocuments());
    await act(async () => {});

    let uploadPromise;
    act(() => {
      uploadPromise = result.current.upload(new File([""], "f.pdf"));
    });
    expect(result.current.uploading).toBe(true);

    await act(async () => {
      await uploadPromise;
    });
    expect(result.current.uploading).toBe(false);
    expect(result.current.documents).toEqual(["f.pdf"]);
  });

  it("calls DELETE and refreshes list on remove", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ documents: ["f.pdf"] }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ documents: [] }),
      });

    const { result } = renderHook(() => useDocuments());
    await act(async () => {});
    await act(async () => {
      await result.current.remove("f.pdf");
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/documents\/f\.pdf$/),
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(result.current.documents).toEqual([]);
  });

  it("sets error when upload fetch rejects", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ documents: [] }),
      })
      .mockRejectedValueOnce(new Error("network error"));

    const { result } = renderHook(() => useDocuments());
    await act(async () => {});
    await act(async () => {
      await result.current.upload(new File([""], "f.pdf"));
    });

    expect(result.current.error).toBe("network error");
  });
});
