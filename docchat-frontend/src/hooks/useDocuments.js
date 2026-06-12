import { useState, useEffect, useCallback } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    const res = await fetch(`${API_URL}/documents/`);
    if (!res.ok) throw new Error(`Failed to list documents: ${res.status}`);
    const data = await res.json();
    setDocuments(data.documents);
  }, []);

  useEffect(() => {
    fetchDocuments().catch((err) => setError(err.message));
  }, [fetchDocuments]);

  const upload = useCallback(
    async (file) => {
      setError(null);
      setUploading(true);
      try {
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${API_URL}/documents/upload`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.detail ?? `Upload failed: ${res.status}`);
        }
        await fetchDocuments();
      } catch (err) {
        setError(err.message);
      } finally {
        setUploading(false);
      }
    },
    [fetchDocuments],
  );

  const remove = useCallback(
    async (filename) => {
      setError(null);
      try {
        const res = await fetch(
          `${API_URL}/documents/${encodeURIComponent(filename)}`,
          { method: "DELETE" },
        );
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.detail ?? `Delete failed: ${res.status}`);
        }
        await fetchDocuments();
      } catch (err) {
        setError(err.message);
      }
    },
    [fetchDocuments],
  );

  return { documents, uploading, error, upload, remove };
}
