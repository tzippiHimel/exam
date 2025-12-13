import React from 'react';
import '../App.css';
import './ResultsDashboard.css';

function ResultsDashboard({ results, onReset }) {
  const getScoreColor = (score) => {
    if (score >= 90) return '#28a745';
    if (score >= 70) return '#ffc107';
    if (score >= 50) return '#fd7e14';
    return '#dc3545';
  };

  const getGradeLetter = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  return (
    <div className="step-container">
      <h2>Grading Results</h2>

      {/* Final Score Card */}
      <div className="final-score-card">
        <div className="score-circle" style={{ borderColor: getScoreColor(results.final_score) }}>
          <div className="score-value" style={{ color: getScoreColor(results.final_score) }}>
            {results.final_score.toFixed(1)}%
          </div>
          <div className="score-grade">{getGradeLetter(results.final_score)}</div>
        </div>
        <div className="score-details">
          <h3>Final Score</h3>
          <p>
            {results.correct_answers} out of {results.total_questions} questions correct
          </p>
        </div>
      </div>

      {/* Per-Question Results */}
      <div className="results-section">
        <h3 style={{ marginBottom: '1.5rem' }}>Question-by-Question Results</h3>
        <div className="results-grid">
          {results.question_grades.map((grade, idx) => (
            <div key={idx} className="result-card">
              <div className="result-header">
                <span className="result-question-number">Question {grade.question_index + 1}</span>
                <span
                  className="result-score-badge"
                  style={{ backgroundColor: getScoreColor(grade.score) }}
                >
                  {grade.score.toFixed(1)}%
                </span>
              </div>

              <div className="result-content">
                <div className="result-item">
                  <strong>Question:</strong>
                  <p>{grade.question}</p>
                </div>

                <div className="result-item">
                  <strong>Correct Answer:</strong>
                  <p className="correct-answer">{grade.correct_answer}</p>
                </div>

                <div className="result-item">
                  <strong>Your Answer:</strong>
                  <p className={grade.is_correct ? 'correct-answer' : 'incorrect-answer'}>
                    {grade.student_answer}
                  </p>
                </div>

                <div className="result-item">
                  <strong>Explanation:</strong>
                  <p className="explanation-text">{grade.explanation}</p>
                </div>

                {grade.is_correct && (
                  <div className="correct-badge">✓ Correct</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={onReset}
        className="btn btn-secondary"
        style={{ marginTop: '2rem', width: '100%' }}
      >
        Grade Another Exam
      </button>
    </div>
  );
}

export default ResultsDashboard;

