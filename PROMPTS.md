# Gemini API Prompts

This document contains the prompts used for exam parsing and answer grading.

## Exam Parsing Prompt

**Purpose**: Extract structured questions and answers from OCR-extracted text.

**Prompt Template**:
```
You are an expert at parsing exam documents. Extract all questions and their correct answers from the following exam text.

EXAM TEXT:
{extracted_text}

INSTRUCTIONS:
1. Identify all questions in the exam
2. For each question, extract the question text and its correct answer
3. Return ONLY a valid JSON array in this exact format:
[
  {
    "question": "Question text here",
    "correct_answer": "Correct answer text here"
  }
]

IMPORTANT:
- Return ONLY the JSON array, no additional text
- Ensure all questions are numbered or clearly separated
- If a question has multiple parts, include all parts in the question text
- Be precise with the correct answers
- If you cannot parse the exam, return an empty array: []

JSON OUTPUT:
```

**Expected Response Format**:
```json
[
  {
    "question": "What is the capital of France?",
    "correct_answer": "Paris"
  },
  {
    "question": "Explain the concept of photosynthesis.",
    "correct_answer": "Photosynthesis is the process by which plants convert light energy into chemical energy..."
  }
]
```

## Answer Grading Prompt

**Purpose**: Grade a student's answer against the correct answer.

**Prompt Template**:
```
You are an expert exam grader. Grade the student's answer against the correct answer.

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
{
  "score": 85.5,
  "is_correct": false,
  "explanation": "Brief explanation of why this score was given"
}

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

JSON OUTPUT:
```

**Expected Response Format**:
```json
{
  "score": 85.5,
  "is_correct": false,
  "explanation": "The student's answer demonstrates good understanding but misses a key detail about the process."
}
```

## Prompt Engineering Best Practices

1. **Clear Instructions**: Prompts include explicit instructions and formatting requirements
2. **Structured Output**: JSON format is enforced for reliable parsing
3. **Error Handling**: Prompts include fallback instructions for edge cases
4. **Context Setting**: Role-based prompts ("You are an expert...") improve AI performance
5. **Examples**: Scoring guidelines provide clear criteria for consistent grading

## Customization

To customize prompts, edit:
- `backend/app/services/gemini_service.py` - `parse_exam_text()` function
- `backend/app/services/gemini_service.py` - `grade_answer()` function

## Testing Prompts

You can test prompts directly using the Gemini API:

```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel("gemini-pro")

response = model.generate_content("Your prompt here")
print(response.text)
```

