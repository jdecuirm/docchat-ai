import SourcesAccordion from "./SourcesAccordion";

export default function AIBubble({ message }) {
  return (
    <div className="max-w-[80%] self-start">
      <div
        className={[
          "rounded-xl px-4 py-3 text-sm bg-ai-bg",
          message.isError ? "text-red-400" : "text-ai-text",
        ].join(" ")}
      >
        {message.content || <span className="opacity-50">…</span>}
      </div>
      <SourcesAccordion sources={message.sources} />
    </div>
  );
}
