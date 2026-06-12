import { useState } from "react";

const ALLOWED = [".pdf", ".docx"];

function getExtension(filename) {
  return filename.slice(filename.lastIndexOf(".")).toLowerCase();
}

export default function DropZone({ onUpload }) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState(null);

  function validate(file) {
    if (!ALLOWED.includes(getExtension(file.name))) {
      setError("Only PDF and DOCX files are allowed.");
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File exceeds the 10 MB limit.");
      return false;
    }
    setError(null);
    return true;
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && validate(file)) onUpload(file);
  }

  function handleDragOver(e) {
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave() {
    setIsDragging(false);
  }

  function handleInputChange(e) {
    const file = e.target.files[0];
    if (file && validate(file)) onUpload(file);
    e.target.value = "";
  }

  return (
    <div>
      <label
        data-testid="drop-zone"
        className={[
          "flex flex-col items-center justify-center gap-2 p-4 rounded-lg cursor-pointer",
          "border-2 border-dashed transition-colors",
          isDragging
            ? "border-accent bg-surface-raised"
            : "border-accent-dim hover:border-accent",
        ].join(" ")}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          accept=".pdf,.docx"
          className="sr-only"
          onChange={handleInputChange}
        />
        <span className="text-2xl">📂</span>
        <span className="text-text-muted text-sm text-center">
          Drop PDF / DOCX here
        </span>
        <span className="text-accent text-sm font-medium">
          or click to browse
        </span>
      </label>
      {error && <p className="mt-2 text-red-400 text-xs">{error}</p>}
    </div>
  );
}
