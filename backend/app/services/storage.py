"""
In-memory storage for exams and results.
"""
import uuid
from typing import Dict, Optional
from app.models import QuestionAnswer

# In-memory storage
_exams: Dict[str, Dict] = {}


def generate_exam_id() -> str:
    """Generate unique exam ID."""
    return str(uuid.uuid4())


def store_exam(exam_id: str, file_bytes: bytes, file_type: str, extracted_text: str):
    """Store exam data."""
    _exams[exam_id] = {
        "exam_id": exam_id,
        "file_bytes": file_bytes,
        "file_type": file_type,
        "extracted_text": extracted_text,
        "questions": None,
        "results": None
    }


def get_exam(exam_id: str) -> Optional[Dict]:
    """Get exam data by ID."""
    return _exams.get(exam_id)


def store_parsed_questions(exam_id: str, questions: List[QuestionAnswer]):
    """Store parsed questions for an exam."""
    if exam_id in _exams:
        _exams[exam_id]["questions"] = questions


def get_parsed_questions(exam_id: str) -> Optional[List[QuestionAnswer]]:
    """Get parsed questions for an exam."""
    exam = _exams.get(exam_id)
    return exam.get("questions") if exam else None


def store_results(exam_id: str, results: Dict):
    """Store grading results."""
    if exam_id in _exams:
        _exams[exam_id]["results"] = results


def get_results(exam_id: str) -> Optional[Dict]:
    """Get grading results for an exam."""
    exam = _exams.get(exam_id)
    return exam.get("results") if exam else None

