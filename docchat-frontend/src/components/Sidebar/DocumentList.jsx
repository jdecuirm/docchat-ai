import DocumentItem from "./DocumentItem";

export default function DocumentList({ documents, onDelete }) {
  if (documents.length === 0) {
    return (
      <p className="text-text-muted text-xs text-center py-4">
        No documents uploaded yet.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {documents.map((filename) => (
        <DocumentItem key={filename} filename={filename} onDelete={onDelete} />
      ))}
    </div>
  );
}
