"""
Gemini API service for exam parsing and answer grading.
"""
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from app.config import settings
from app.models import QuestionAnswer, QuestionGrade

logger = logging.getLogger(__name__)

# Initialize Gemini client
genai.configure(api_key=settings.GEMINI_API_KEY)


def parse_exam_text(text: str) -> List[QuestionAnswer]:
    """
    Parse exam text into structured questions and answers using Gemini.
    
    Args:
        text: Raw OCR-extracted text from exam
        
    Returns:
        List of QuestionAnswer objects
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    prompt = f"""You are an expert at parsing exam documents. Extract all questions and their correct answers from the following exam text.

EXAM TEXT:
{text}

INSTRUCTIONS:
1. Identify all questions in the exam
2. For each question, extract the question text and its correct answer
3. Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "Question text here",
    "correct_answer": "Correct answer text here"
  }}
]

IMPORTANT:
- Return ONLY the JSON array, no additional text
- Ensure all questions are numbered or clearly separated
- If a question has multiple parts, include all parts in the question text
- Be precise with the correct answers
- If you cannot parse the exam, return an empty array: []

JSON OUTPUT:"""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        parsed_data = json.loads(response_text)
        
        if not isinstance(parsed_data, list):
            raise ValueError("Expected JSON array")
        
        questions = []
        for item in parsed_data:
            if "question" in item and "correct_answer" in item:
                questions.append(QuestionAnswer(
                    question=item["question"],
                    correct_answer=item["correct_answer"]
                ))
        
        logger.info(f"Parsed {len(questions)} questions from exam")
        return questions
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response text: {response_text[:500]}")
        raise ValueError(f"Failed to parse exam: Invalid JSON response from AI")
    except Exception as e:
        logger.error(f"Error parsing exam with Gemini: {str(e)}")
        raise ValueError(f"Failed to parse exam: {str(e)}")


def grade_answer(
    question: str,
    correct_answer: str,
    student_answer: str
) -> Dict[str, Any]:
    """
    Grade a student's answer against the correct answer using Gemini.
    
    Args:
        question: The question text
        correct_answer: The correct answer
        student_answer: The student's answer
        
    Returns:
        Dictionary with score, is_correct, and explanation
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    prompt = f"""You are an expert exam grader. Grade the student's answer against the correct answer.

QUESTION:
{question}

CORRECT ANSWER:
{correct_answer}

STUDENT ANSWER:
{student_answer}

INSTRUCTIONS:
1. Compare the student's answer to the correct answer
2. Consider partial credit for partially correct answers
3. Be fair but strict - only give full credit for fully correct answers
4. Return ONLY a valid JSON object in this exact format:
{{
  "score": 85.5,
  "is_correct": false,
  "explanation": "Brief explanation of why this score was given"
}}

SCORING GUIDELINES:
- 100: Perfect match or equivalent correct answer
- 80-99: Mostly correct with minor issues
- 60-79: Partially correct
- 40-59: Some relevant content but mostly incorrect
- 20-39: Minimal relevant content
- 0-19: Completely incorrect or no answer

IMPORTANT:
- Return ONLY the JSON object, no additional text
- Score should be a number between 0 and 100
- is_correct should be true only if score is 100
- Explanation should be concise (1-2 sentences)

JSON OUTPUT:"""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Validate and normalize
        score = float(result.get("score", 0))
        score = max(0, min(100, score))  # Clamp between 0-100
        is_correct = result.get("is_correct", False) or score == 100
        explanation = result.get("explanation", "No explanation provided")
        
        return {
            "score": score,
            "is_correct": is_correct,
            "explanation": explanation
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response text: {response_text[:500]}")
        raise ValueError(f"Failed to grade answer: Invalid JSON response from AI")
    except Exception as e:
        logger.error(f"Error grading answer with Gemini: {str(e)}")
        raise ValueError(f"Failed to grade answer: {str(e)}")

