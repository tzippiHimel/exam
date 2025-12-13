"""
Exam-related API endpoints.
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.models import (
    ExamUploadResponse,
    ExamParseRequest,
    ExamParseResponse,
    GradeRequest,
    GradeResponse,
    QuestionGrade
)
from app.services import ocr_service, gemini_service, grading_service, storage

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=ExamUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_exam(file: UploadFile = File(...)):
    """
    Upload a solved exam (PDF, image, or text file).
    """
    try:
        # Validate file type
        file_extension = None
        for ext in [".pdf", ".png", ".jpg", ".jpeg", ".txt"]:
            if file.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: PDF, PNG, JPG, TXT"
            )
        
        # Read file
        file_bytes = await file.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        
        if file_size_mb > 10:  # Max 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: 10MB"
            )
        
        # Generate exam ID
        exam_id = storage.generate_exam_id()
        
        # Extract text using OCR
        logger.info(f"Extracting text from {file.filename} (exam_id: {exam_id})")
        extracted_text = ocr_service.extract_text_from_file(file_bytes, file_extension)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from file. Please ensure the file is readable."
            )
        
        # Store exam
        storage.store_exam(exam_id, file_bytes, file_extension, extracted_text)
        
        logger.info(f"Exam uploaded successfully: {exam_id}")
        
        return ExamUploadResponse(
            exam_id=exam_id,
            message="Exam uploaded successfully",
            file_type=file_extension,
            file_size=len(file_bytes)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload exam: {str(e)}"
        )


@router.post("/{exam_id}/parse", response_model=ExamParseResponse)
async def parse_exam(exam_id: str):
    """
    Parse uploaded exam into structured questions and answers.
    """
    try:
        # Get exam
        exam = storage.get_exam(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found"
            )
        
        # Check if already parsed
        existing_questions = storage.get_parsed_questions(exam_id)
        if existing_questions:
            logger.info(f"Returning cached parsed questions for exam {exam_id}")
            return ExamParseResponse(
                exam_id=exam_id,
                questions=existing_questions,
                total_questions=len(existing_questions)
            )
        
        # Parse using Gemini
        logger.info(f"Parsing exam {exam_id} with Gemini")
        extracted_text = exam["extracted_text"]
        questions = gemini_service.parse_exam_text(extracted_text)
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse exam. No questions found. Please ensure the exam format is clear."
            )
        
        # Store parsed questions
        storage.store_parsed_questions(exam_id, questions)
        
        logger.info(f"Parsed {len(questions)} questions for exam {exam_id}")
        
        return ExamParseResponse(
            exam_id=exam_id,
            questions=questions,
            total_questions=len(questions)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error parsing exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse exam: {str(e)}"
        )


@router.post("/{exam_id}/grade", response_model=GradeResponse)
async def grade_exam(exam_id: str, request: GradeRequest):
    """
    Grade student answers against the exam.
    """
    try:
        # Validate exam_id matches
        if request.exam_id != exam_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam ID mismatch"
            )
        
        # Get parsed questions
        questions = storage.get_parsed_questions(exam_id)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exam {exam_id} not parsed. Please parse the exam first."
            )
        
        # Grade each answer
        question_grades = []
        for student_answer in request.student_answers:
            question_idx = student_answer.question_index
            
            if question_idx >= len(questions):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question index {question_idx} out of range. Exam has {len(questions)} questions."
                )
            
            question = questions[question_idx]
            
            # Grade using Gemini
            logger.info(f"Grading question {question_idx} for exam {exam_id}")
            grade_result = gemini_service.grade_answer(
                question.question,
                question.correct_answer,
                student_answer.answer
            )
            
            question_grade = QuestionGrade(
                question_index=question_idx,
                question=question.question,
                correct_answer=question.correct_answer,
                student_answer=student_answer.answer,
                score=grade_result["score"],
                is_correct=grade_result["is_correct"],
                explanation=grade_result["explanation"]
            )
            question_grades.append(question_grade)
        
        # Calculate final grade
        final_score = grading_service.calculate_final_grade(question_grades)
        correct_count = grading_service.count_correct_answers(question_grades)
        
        # Store results
        results = {
            "question_grades": question_grades,
            "final_score": final_score,
            "correct_count": correct_count
        }
        storage.store_results(exam_id, results)
        
        logger.info(f"Graded exam {exam_id}: {final_score}% ({correct_count}/{len(questions)} correct)")
        
        return GradeResponse(
            exam_id=exam_id,
            question_grades=question_grades,
            final_score=final_score,
            total_questions=len(questions),
            correct_answers=correct_count
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error grading exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grade exam: {str(e)}"
        )


@router.get("/{exam_id}/results", response_model=GradeResponse)
async def get_results(exam_id: str):
    """
    Get grading results for an exam.
    """
    results = storage.get_results(exam_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No results found for exam {exam_id}"
        )
    
    questions = storage.get_parsed_questions(exam_id)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam {exam_id} not found"
        )
    
    return GradeResponse(
        exam_id=exam_id,
        question_grades=results["question_grades"],
        final_score=results["final_score"],
        total_questions=len(questions),
        correct_answers=results["correct_count"]
    )

