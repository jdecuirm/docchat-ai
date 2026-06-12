import { useEffect, useRef } from "react";
import Message from "./Message";

export default function MessageList({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-text-muted text-sm">
          Ask a question to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto flex flex-col gap-4 px-4 py-4">
      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
