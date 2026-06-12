import { useState } from "react";

export default function ChatInput({ onSend, streaming }) {
  const [value, setValue] = useState("");

  const disabled = streaming || value.trim() === "";

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || streaming) return;
    onSend(trimmed);
    setValue("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="flex items-end gap-2 p-3 border-t border-accent-dim bg-surface">
      <textarea
        className={[
          "flex-1 resize-none rounded-lg px-3 py-2 text-sm",
          "bg-surface-raised text-text-primary",
          "placeholder:text-text-muted",
          "focus:outline-none focus:ring-1 focus:ring-accent",
          "max-h-28 overflow-y-auto",
        ].join(" ")}
        rows={1}
        placeholder="Ask anything…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={streaming}
        aria-label="Chat input"
      />
      <button
        className={[
          "shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
          disabled
            ? "bg-surface-raised text-text-muted cursor-not-allowed"
            : "bg-accent text-white hover:opacity-90",
        ].join(" ")}
        onClick={submit}
        disabled={disabled}
        aria-label="Send"
      >
        Send
      </button>
    </div>
  );
}
