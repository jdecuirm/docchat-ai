import { useState } from "react";
import SourceItem from "./SourceItem";

export default function SourcesAccordion({ sources }) {
  const [open, setOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-2 rounded-md bg-citations-bg border border-amber-200">
      <button
        className="flex w-full items-center justify-between px-3 py-2 text-xs font-medium text-citations-accent"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <span>📎 Sources ({sources.length})</span>
        <span aria-hidden="true">{open ? "▴" : "▾"}</span>
      </button>
      {open && (
        <div className="border-t border-amber-200">
          {sources.map((source, i) => (
            <SourceItem
              key={`${source.source_filename}-${source.page_number}`}
              source={source}
              index={i}
            />
          ))}
        </div>
      )}
    </div>
  );
}
