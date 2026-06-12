export default function SourceItem({ source, index }) {
  return (
    <div className="flex items-center justify-between gap-2 py-1 px-2 text-xs text-text-muted">
      <span className="flex items-center gap-1 min-w-0">
        <span className="shrink-0">[{index + 1}]</span>
        <span className="text-text-primary truncate">{source.filename}</span>
        <span className="shrink-0">— page {source.page}</span>
      </span>
      <span className="shrink-0">score: {source.score.toFixed(2)}</span>
    </div>
  );
}
