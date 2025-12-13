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
      <p>Click the button below to parse the uploaded exam into questions and answers.</p>
      <button
        onClick={handleParse}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? 'Parsing...' : 'Parse Exam'}
      </button>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default App;

