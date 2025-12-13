"""
Pydantic models for request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionAnswer(BaseModel):
    """Single question-answer pair from exam."""
    question: str = Field(..., description="The question text")
    correct_answer: str = Field(..., description="The correct answer")


class ExamParseRequest(BaseModel):
    """Request to parse an uploaded exam."""
    exam_id: str = Field(..., description="Unique exam identifier")


class ExamParseResponse(BaseModel):
    """Response containing parsed questions and answers."""
    exam_id: str
    questions: List[QuestionAnswer] = Field(..., description="List of parsed questions")
    total_questions: int


class StudentAnswer(BaseModel):
    """Student's answer to a question."""
    question_index: int = Field(..., ge=0, description="Index of the question (0-based)")
    answer: str = Field(..., description="Student's answer text")


class GradeRequest(BaseModel):
    """Request to grade student answers."""
    exam_id: str = Field(..., description="Unique exam identifier")
    student_answers: List[StudentAnswer] = Field(..., description="List of student answers")


class QuestionGrade(BaseModel):
    """Grading result for a single question."""
    question_index: int
    question: str
    correct_answer: str
    student_answer: str
    score: float = Field(..., ge=0, le=100, description="Score out of 100")
    is_correct: bool
    explanation: str = Field(..., description="Brief explanation of the grading")


class GradeResponse(BaseModel):
    """Response containing grading results."""
    exam_id: str
    question_grades: List[QuestionGrade]
    final_score: float = Field(..., ge=0, le=100, description="Final score out of 100")
    total_questions: int
    correct_answers: int


class ExamUploadResponse(BaseModel):
    """Response after uploading an exam."""
    exam_id: str
    message: str
    file_type: str
    file_size: int

