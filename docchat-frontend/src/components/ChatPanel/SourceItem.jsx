export default function SourceItem({ source, index }) {
  return (
    <div className="flex items-center justify-between gap-2 py-1 px-2 text-xs text-text-muted">
      <span className="truncate">
        [{index + 1}]{" "}
        <span className="text-text-primary">{source.filename}</span> — page{" "}
        {source.page}
      </span>
      <span className="shrink-0">score: {source.score.toFixed(2)}</span>
    </div>
  );
}
