import { useState, useCallback } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const MAX_HISTORY_TURNS = 3;

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);

  const updateLastAI = (updater) => {
    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = updater(updated[updated.length - 1]);
      return updated;
    });
  };

  const sendMessage = useCallback(
    async (question) => {
      // Capture history BEFORE appending the new placeholder messages.
      const history = messages
        .slice(-(MAX_HISTORY_TURNS * 2))
        .filter((m) => m.content && !m.isError)
        .map((m) => ({
          role: m.role === "ai" ? "assistant" : "user",
          content: m.content,
        }));

      setMessages((prev) => [
        ...prev,
        { role: "user", content: question, id: crypto.randomUUID() },
        { role: "ai", content: "", sources: [], id: crypto.randomUUID() },
      ]);
      setStreaming(true);

      try {
        const res = await fetch(`${API_URL}/chat/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, history }),
        });

        if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let pendingEvent = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop();

          for (const line of lines) {
            if (line === "") {
              pendingEvent = null;
            } else if (line.startsWith("event: ")) {
              pendingEvent = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              const payload = line.slice(6);
              if (pendingEvent === "citations") {
                const sources = JSON.parse(payload);
                updateLastAI((msg) => ({ ...msg, sources }));
              } else if (pendingEvent === "error") {
                const { message } = JSON.parse(payload);
                updateLastAI((msg) => ({
                  ...msg,
                  content: `Error: ${message}`,
                  isError: true,
                }));
              } else {
                updateLastAI((msg) => ({
                  ...msg,
                  content: msg.content + payload,
                }));
              }
            }
          }
        }

        // Flush remaining buffer content when stream ends without trailing \n
        if (buffer.trim()) {
          if (buffer.startsWith("data: ")) {
            const payload = buffer.slice(6);
            if (pendingEvent === "citations") {
              const sources = JSON.parse(payload);
              updateLastAI((msg) => ({ ...msg, sources }));
            } else if (pendingEvent === "error") {
              const { message } = JSON.parse(payload);
              updateLastAI((msg) => ({
                ...msg,
                content: `Error: ${message}`,
                isError: true,
              }));
            } else {
              updateLastAI((msg) => ({
                ...msg,
                content: msg.content + payload,
              }));
            }
          }
        }
      } catch (err) {
        updateLastAI((msg) => ({
          ...msg,
          content: `Error: ${err.message}`,
          isError: true,
        }));
      } finally {
        setStreaming(false);
      }
    },
    [messages], // messages is read for history — must be a dep
  );

  return { messages, streaming, sendMessage };
}
