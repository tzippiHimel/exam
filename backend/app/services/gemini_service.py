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
    
    # Log the input text for debugging (first 1000 chars)
    logger.info(f"Parsing exam text (length: {len(text)} chars)")
    logger.debug(f"Exam text preview: {text[:1000]}")
    
    # Check if text is too short or empty
    if not text or len(text.strip()) < 20:
        logger.warning(f"Exam text is too short: {len(text)} characters")
        raise ValueError("Exam text is too short or empty. Please ensure the file contains readable exam content.")
    
    prompt = f"""You are an expert at parsing exam documents. Extract all questions and their correct answers from the following exam text.

EXAM TEXT:
{text}

INSTRUCTIONS:
1. Identify ALL questions in the exam (look for numbered questions, question marks, or clear question patterns)
2. For each question, extract the complete question text and its correct answer
3. The exam may be in Hebrew, English, or mixed languages - parse it accordingly
4. Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "Question text here",
    "correct_answer": "Correct answer text here"
  }},
  {{
    "question": "Another question",
    "correct_answer": "Another answer"
  }}
]

IMPORTANT:
- Return ONLY the JSON array, no additional text before or after
- Look for questions even if they're not perfectly formatted
- Questions may be numbered (1., 2., Question 1, etc.) or unnumbered
- Answers may appear after each question or at the end of the exam
- If a question has multiple parts (a, b, c), you can either:
  * Include all parts in one question text, OR
  * Create separate question entries for each part
- Be flexible with formatting - extract questions even if the format is imperfect
- If you find at least one question, return it. Only return empty array [] if you truly cannot find ANY questions.

JSON OUTPUT:"""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"Sending request to Gemini API using model: {settings.GEMINI_MODEL}")
        
        # Configure generation with timeout and retry
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=8192,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            request_options={'timeout': 30}
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        logger.debug(f"Raw Gemini response (first 500 chars): {response_text[:500]}")
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Try to extract JSON if there's extra text
        # Look for JSON array pattern
        json_start = response_text.find('[')
        json_end = response_text.rfind(']')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            response_text = response_text[json_start:json_end+1]
        
        # Parse JSON
        parsed_data = json.loads(response_text)
        
        if not isinstance(parsed_data, list):
            logger.error(f"Expected JSON array but got: {type(parsed_data)}")
            raise ValueError("Expected JSON array")
        
        logger.info(f"Gemini returned {len(parsed_data)} items in JSON array")
        
        questions = []
        for i, item in enumerate(parsed_data):
            if not isinstance(item, dict):
                logger.warning(f"Item {i} is not a dictionary, skipping")
                continue
            if "question" in item and "correct_answer" in item:
                questions.append(QuestionAnswer(
                    question=str(item["question"]).strip(),
                    correct_answer=str(item["correct_answer"]).strip()
                ))
            else:
                logger.warning(f"Item {i} missing 'question' or 'correct_answer' keys: {item.keys()}")
        
        if len(questions) == 0 and len(parsed_data) > 0:
            logger.error(f"Parsed {len(parsed_data)} items but none had valid question/answer format")
            logger.error(f"Sample item: {parsed_data[0] if parsed_data else 'N/A'}")
            raise ValueError("Gemini returned data but no valid questions were found. The exam format may not be recognized.")
        
        logger.info(f"Successfully parsed {len(questions)} questions from exam")
        return questions
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response text (first 1000 chars): {response_text[:1000]}")
        raise ValueError(f"Failed to parse exam: Invalid JSON response from AI. Response: {response_text[:200]}")
    except Exception as e:
        logger.error(f"Error parsing exam with Gemini: {str(e)}", exc_info=True)
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

