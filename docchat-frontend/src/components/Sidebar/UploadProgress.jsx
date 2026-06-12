export default function UploadProgress() {
  return (
    <div className="py-3">
      <p className="text-text-muted text-xs mb-2">Uploading…</p>
      <div className="h-1 rounded-full bg-surface-raised overflow-hidden">
        <div className="h-full w-1/2 bg-accent rounded-full animate-[slide_1.2s_ease-in-out_infinite]" />
      </div>
    </div>
  );
}
