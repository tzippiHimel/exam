"""
Grading service for calculating final scores and aggregating results.
"""
import logging
from typing import List
from app.models import QuestionAnswer, StudentAnswer, QuestionGrade

logger = logging.getLogger(__name__)


def calculate_final_grade(question_grades: List[QuestionGrade]) -> float:
    """
    Calculate final grade as average of all question scores.
    
    Args:
        question_grades: List of graded questions
        
    Returns:
        Final score (0-100)
    """
    if not question_grades:
        return 0.0
    
    total_score = sum(grade.score for grade in question_grades)
    final_score = total_score / len(question_grades)
    
    return round(final_score, 2)


def count_correct_answers(question_grades: List[QuestionGrade]) -> int:
    """
    Count number of fully correct answers.
    
    Args:
        question_grades: List of graded questions
        
    Returns:
        Number of correct answers
    """
    return sum(1 for grade in question_grades if grade.is_correct)

