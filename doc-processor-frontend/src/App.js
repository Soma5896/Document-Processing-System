import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = acceptedFiles => {
    setFile(acceptedFiles[0]);
    setResult(null);
    setError("");
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:8000/process/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h2>📄 Document Processor</h2>
      <div {...getRootProps()} style={{
        border: "2px dashed #ccc",
        padding: "1rem",
        borderRadius: "8px",
        marginBottom: "1rem",
        backgroundColor: "#f9f9f9"
      }}>
        <input {...getInputProps()} />
        <p>{file ? file.name : "Drag & drop or click to select a file"}</p>
      </div>

      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? "Processing..." : "Upload & Analyze"}
      </button>

      {error && <p style={{ color: "red" }}>❌ {error}</p>}

      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h3>✅ Results</h3>
          <pre><strong>Text:</strong> {result.extracted_text}</pre>
          <p><strong>Category:</strong> {result.classification.category} ({(result.classification.confidence * 100).toFixed(2)}%)</p>
          
          <h4>Entities</h4>
          <pre>{JSON.stringify(result.entities, null, 2)}</pre>

          {Object.keys(result.specific_data || {}).length > 0 && (
            <>
              <h4>Specific Info</h4>
              <pre>{JSON.stringify(result.specific_data, null, 2)}</pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
