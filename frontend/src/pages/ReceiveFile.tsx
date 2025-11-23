import { useState } from "react";

const ReceiveFile = () => {
  const [code, setCode] = useState("");
  const [file, setFile] = useState<{ name: string; url: string; size?: number } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) {
      setError("Please enter the receive code.");
      return;
    }
    setLoading(true);
    setError("");
    setFile(null);
    try {
      const res = await fetch(`/api/files/${encodeURIComponent(code.trim())}`);
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `File not found (status ${res.status})`);
      }
      const data = await res.json();
      // Expecting { name, url, size? } from the backend
      setFile(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch file.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Receive file</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <span className="text-sm">Enter receive code</span>
          <input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="e.g. AB12-CD34"
            className="mt-1 block w-full border rounded px-3 py-2"
            aria-label="receive code"
          />
        </label>

        <div className="flex gap-2">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded"
            disabled={loading}
          >
            {loading ? "Looking up..." : "Retrieve file"}
          </button>
          <button
            type="button"
            className="px-4 py-2 border rounded"
            onClick={() => {
              setCode("");
              setFile(null);
              setError("");
            }}
          >
            Clear
          </button>
        </div>
      </form>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {file && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <p className="font-medium">File ready:</p>
          <p className="mt-1">
            <strong>{file.name}</strong>
            {file.size ? <span className="ml-2 text-sm text-gray-600">({file.size} bytes)</span> : null}
          </p>
          <div className="mt-3 flex gap-2">
            <a
              href={file.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 bg-green-600 text-white rounded"
              download={file.name}
            >
              Download
            </a>
            <a
              href={file.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 border rounded"
            >
              Open in new tab
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReceiveFile;