export default function DocumentItem({ filename, onDelete }) {
  return (
    <div className="flex items-center justify-between gap-2 px-3 py-2 rounded-md bg-surface-raised group">
      <span
        className="text-text-primary text-sm truncate flex-1"
        title={filename}
      >
        📄 {filename}
      </span>
      <button
        onClick={() => onDelete(filename)}
        className="text-accent-muted hover:text-red-400 text-xs shrink-0 transition-colors"
        aria-label={`Delete ${filename}`}
      >
        ✕
      </button>
    </div>
  );
}
