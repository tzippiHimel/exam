import React, { useState } from 'react';
import '../App.css';
import './StudentAnswers.css';

function StudentAnswers({ apiBaseUrl, examId, questions, onGraded }) {
  const [answers, setAnswers] = useState(
    questions.map((q, idx) => ({ question_index: idx, answer: '' }))
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnswerChange = (index, value) => {
    const newAnswers = [...answers];
    newAnswers[index].answer = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/exams/${examId}/grade`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          exam_id: examId,
          student_answers: answers,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Grading failed');
      }

      const data = await response.json();
      onGraded(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step-container">
      <h2>Step 3: Submit Student Answers</h2>
      <p style={{ marginBottom: '1.5rem', color: '#666' }}>
        Enter the student's answers for each question below.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="answers-container">
          {questions.map((question, idx) => (
            <div key={idx} className="question-card">
              <div className="question-header">
                <span className="question-number">Question {idx + 1}</span>
              </div>
              <div className="question-text">
                <strong>Q:</strong> {question.question}
              </div>
              <div className="answer-input-container">
                <label htmlFor={`answer-${idx}`}>Your Answer:</label>
                <textarea
                  id={`answer-${idx}`}
                  value={answers[idx].answer}
                  onChange={(e) => handleAnswerChange(idx, e.target.value)}
                  className="answer-textarea"
                  rows="3"
                  placeholder="Enter your answer here..."
                  required
                />
              </div>
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary"
          style={{ marginTop: '2rem', width: '100%' }}
        >
          {loading ? 'Grading...' : 'Submit Answers for Grading'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default StudentAnswers;

