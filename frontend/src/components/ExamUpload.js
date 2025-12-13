import React, { useState } from 'react';
import '../App.css';
import './ExamUpload.css';

function ExamUpload({ apiBaseUrl, onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiBaseUrl}/api/exams/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setSuccess(`Exam uploaded successfully! Exam ID: ${data.exam_id}`);
      onUploaded(data.exam_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step-container">
      <h2>Step 1: Upload Solved Exam</h2>
      <p style={{ marginBottom: '1.5rem', color: '#666' }}>
        Upload a solved exam (PDF, image, or text file) that contains questions and their correct answers.
      </p>

      <form onSubmit={handleUpload}>
        <div className="upload-area">
          <input
            type="file"
            id="file-upload"
            accept=".pdf,.png,.jpg,.jpeg,.txt"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-upload" className="file-label">
            {file ? file.name : 'Choose File'}
          </label>
          <button
            type="button"
            onClick={() => document.getElementById('file-upload').click()}
            className="btn btn-secondary"
            style={{ marginLeft: '1rem' }}
          >
            Browse
          </button>
        </div>

        {file && (
          <div style={{ marginTop: '1rem' }}>
            <p>Selected: <strong>{file.name}</strong></p>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Size: {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || loading}
          className="btn btn-primary"
          style={{ marginTop: '1.5rem' }}
        >
          {loading ? 'Uploading...' : 'Upload Exam'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
    </div>
  );
}

export default ExamUpload;

