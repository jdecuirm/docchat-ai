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
    <aside className="w-72 shrink-0 flex flex-col gap-4 p-4 bg-surface h-full overflow-y-auto">
      <h2 className="text-accent text-xs font-bold uppercase tracking-widest">
        Documents
      </h2>

      {uploading ? <UploadProgress /> : <DropZone onUpload={onUpload} />}

      {uploadError && <p className="text-red-400 text-xs">{uploadError}</p>}

      <DocumentList documents={documents} onDelete={onDelete} />
    </aside>
  );
}
