"""
Unit tests for grading service.
"""
import pytest
from app.services.grading_service import calculate_final_grade, count_correct_answers
from app.models import QuestionGrade


def test_calculate_final_grade():
    """Test final grade calculation."""
    question_grades = [
        QuestionGrade(
            question_index=0,
            question="Q1",
            correct_answer="A",
            student_answer="A",
            score=100.0,
            is_correct=True,
            explanation="Correct"
        ),
        QuestionGrade(
            question_index=1,
            question="Q2",
            correct_answer="B",
            student_answer="B",
            score=100.0,
            is_correct=True,
            explanation="Correct"
        ),
        QuestionGrade(
            question_index=2,
            question="Q3",
            correct_answer="C",
            student_answer="Wrong",
            score=50.0,
            is_correct=False,
            explanation="Partial credit"
        )
    ]
    
    final_score = calculate_final_grade(question_grades)
    assert final_score == pytest.approx(83.33, abs=0.01)


def test_calculate_final_grade_empty():
    """Test final grade with empty list."""
    final_score = calculate_final_grade([])
    assert final_score == 0.0


def test_count_correct_answers():
    """Test counting correct answers."""
    question_grades = [
        QuestionGrade(
            question_index=0,
            question="Q1",
            correct_answer="A",
            student_answer="A",
            score=100.0,
            is_correct=True,
            explanation="Correct"
        ),
        QuestionGrade(
            question_index=1,
            question="Q2",
            correct_answer="B",
            student_answer="Wrong",
            score=50.0,
            is_correct=False,
            explanation="Wrong"
        ),
        QuestionGrade(
            question_index=2,
            question="Q3",
            correct_answer="C",
            student_answer="C",
            score=100.0,
            is_correct=True,
            explanation="Correct"
        )
    ]
    
    correct_count = count_correct_answers(question_grades)
    assert correct_count == 2

