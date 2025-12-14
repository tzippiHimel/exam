import React, { useState } from 'react';
import './App.css';
import ExamUpload from './components/ExamUpload';
import StudentAnswers from './components/StudentAnswers';
import ResultsDashboard from './components/ResultsDashboard';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [examId, setExamId] = useState(null);
  const [parsedQuestions, setParsedQuestions] = useState(null);
  const [gradingResults, setGradingResults] = useState(null);
  const [currentStep, setCurrentStep] = useState('upload'); // upload, parse, grade, results

  const handleExamUploaded = (id) => {
    setExamId(id);
    setCurrentStep('parse');
  };

  const handleExamParsed = (questions) => {
    setParsedQuestions(questions);
    setCurrentStep('grade');
  };

  const handleGradingComplete = (results) => {
    setGradingResults(results);
    setCurrentStep('results');
  };

  const handleReset = () => {
    setExamId(null);
    setParsedQuestions(null);
    setGradingResults(null);
    setCurrentStep('upload');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Exam Grading System</h1>
        <p>Automated exam grading with OCR and AI</p>
      </header>

      <main className="App-main">
        {currentStep === 'upload' && (
          <ExamUpload
            apiBaseUrl={API_BASE_URL}
            onUploaded={handleExamUploaded}
          />
        )}

        {currentStep === 'parse' && examId && (
          <div className="step-container">
            <h2>Step 2: Parse Exam</h2>
            <ParseExam
              apiBaseUrl={API_BASE_URL}
              examId={examId}
              onParsed={handleExamParsed}
            />
          </div>
        )}

        {currentStep === 'grade' && examId && parsedQuestions && (
          <StudentAnswers
            apiBaseUrl={API_BASE_URL}
            examId={examId}
            questions={parsedQuestions}
            onGraded={handleGradingComplete}
          />
        )}

        {currentStep === 'results' && gradingResults && (
          <ResultsDashboard
            results={gradingResults}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  );
}

// Parse Exam Component
function ParseExam({ apiBaseUrl, examId, onParsed }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [extractedText, setExtractedText] = useState(null);
  const [showText, setShowText] = useState(false);
  const [loadingText, setLoadingText] = useState(false);

  const handleViewText = async () => {
    setLoadingText(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/exams/${examId}/text`);
      if (!response.ok) {
        throw new Error('Failed to fetch extracted text');
      }
      const data = await response.json();
      setExtractedText(data);
      setShowText(true);
    } catch (err) {
      setError('Failed to load extracted text: ' + err.message);
    } finally {
      setLoadingText(false);
    }
  };

  const handleParse = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/exams/${examId}/parse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to parse exam');
      }

      const data = await response.json();
      onParsed(data.questions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="parse-container">
      <h2>Step 2: Parse Exam</h2>
      <p style={{ marginBottom: '1.5rem', color: '#666' }}>
        Click the button below to parse the uploaded exam into questions and answers.
      </p>
      
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          onClick={handleViewText}
          disabled={loadingText}
          className="btn btn-secondary"
        >
          {loadingText ? 'Loading...' : '👁️ View Extracted Text'}
        </button>
        <button
          onClick={handleParse}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Parsing...' : 'Parse Exam'}
        </button>
      </div>

      {showText && extractedText && (
        <div style={{
          marginTop: '1.5rem',
          padding: '1rem',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          border: '1px solid #ddd'
        }}>
          <h3 style={{ marginTop: 0 }}>Extracted Text Preview</h3>
          <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>
            <strong>Text Length:</strong> {extractedText.text_length} characters
          </p>
          <div style={{
            maxHeight: '400px',
            overflow: 'auto',
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '4px',
            border: '1px solid #ccc',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            direction: 'ltr',
            textAlign: 'left'
          }}>
            {extractedText.text || extractedText.preview}
          </div>
          <button
            onClick={() => setShowText(false)}
            className="btn btn-secondary"
            style={{ marginTop: '0.5rem' }}
          >
            Hide Text
          </button>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default App;

