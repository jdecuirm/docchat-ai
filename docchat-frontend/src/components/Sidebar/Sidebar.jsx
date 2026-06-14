import DropZone from "./DropZone";
import UploadProgress from "./UploadProgress";
import DocumentList from "./DocumentList";

export default function Sidebar({
  documents,
  uploading,
  uploadError,
  onUpload,
  onDelete,
}) {
  return (
    <aside className="w-72 shrink-0 flex flex-col gap-4 p-4 bg-surface border-r border-accent-dim h-full overflow-y-auto">
      <h2 className="text-accent text-xs font-bold uppercase tracking-widest">
        Documents
      </h2>

      {uploading ? <UploadProgress /> : <DropZone onUpload={onUpload} />}

      {uploadError && <p className="text-red-400 text-xs">{uploadError}</p>}

      <div className="rounded-lg border border-accent-dim bg-surface-raised p-3 text-xs text-text-muted space-y-1">
        <p className="font-semibold text-accent">⚡ Demo</p>
        <p>
          Keep PDFs to <strong>5–10 pages</strong> — larger files may time out
          on the free tier.
        </p>
        <p>
          First upload can take <strong>~30 s</strong> while models warm up.
        </p>
      </div>

      <DocumentList documents={documents} onDelete={onDelete} />
    </aside>
  );
}
