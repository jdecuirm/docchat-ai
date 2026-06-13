import { useState, useRef, useEffect } from "react";

export default function ChatInput({ onSend, streaming }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  const disabled = streaming || value.trim() === "";

  useEffect(() => {
    if (!streaming && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [streaming]);

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || streaming) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function handleInput(e) {
    e.target.style.height = "auto";
    e.target.style.height = `${e.target.scrollHeight}px`;
  }

  return (
    <div className="flex items-end gap-2 p-3 border-t border-accent-dim bg-surface">
      <textarea
        ref={textareaRef}
        className={[
          "flex-1 resize-none rounded-lg px-3 py-2 text-sm",
          "bg-surface-raised text-text-primary",
          "border border-accent-dim placeholder:text-text-muted",
          "focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent",
          "min-h-[2.25rem] max-h-28 overflow-y-auto",
        ].join(" ")}
        placeholder="Ask anything…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
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
