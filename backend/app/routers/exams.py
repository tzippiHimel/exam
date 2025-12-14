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
from app.config import settings

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
        
        # Log processing start
        logger.info(f"Starting processing of {file.filename} (exam_id: {exam_id}, size: {file_size_mb:.1f}MB, type: {file_extension})")
        
        # Extract text using OCR
        logger.info(f"Extracting text from {file.filename} (exam_id: {exam_id})")
        try:
            extracted_text = ocr_service.extract_text_from_file(file_bytes, file_extension)
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from file: {str(e)}. Please ensure the file is readable and in a supported format."
            )
        
        text_length = len(extracted_text.strip()) if extracted_text else 0
        logger.info(f"Extracted {text_length} characters from {file.filename}")
        
        # Log preview of extracted text for debugging
        if extracted_text:
            preview = extracted_text[:200] if len(extracted_text) > 200 else extracted_text
            logger.debug(f"Extracted text preview: {preview}")
        
        if not extracted_text or text_length < 10:
            error_detail = f"Failed to extract text from file. Only {text_length} characters extracted. "
            error_detail += "This might indicate: 1) The file is not readable, 2) OCR failed to detect text, "
            error_detail += "3) The file format is not supported. Please try: "
            error_detail += "- Using a clearer image file (.png, .jpg) with good contrast, "
            error_detail += "- Using a text file (.txt) if possible, "
            error_detail += "- Ensuring the text in the image is clear and not too small."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        
        # Warn if text is very short (might indicate OCR issues)
        if text_length < 100:
            logger.warning(f"Warning: Only {text_length} characters extracted. This might not be enough to parse questions.")
        
        # Store exam
        storage.store_exam(exam_id, file_bytes, file_extension, extracted_text)
        
        logger.info(f"Exam uploaded successfully: {exam_id} (text length: {text_length} chars)")
        
        return ExamUploadResponse(
            exam_id=exam_id,
            message=f"Exam uploaded successfully. Extracted {text_length} characters from {file.filename}",
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
        
        # Log text preview for debugging
        text_preview = extracted_text[:500] if len(extracted_text) > 500 else extracted_text
        logger.info(f"Exam text length: {len(extracted_text)} characters")
        logger.debug(f"Exam text preview: {text_preview}")
        
        try:
            questions = gemini_service.parse_exam_text(extracted_text)
        except ValueError as e:
            # Re-raise ValueError with more context
            error_msg = str(e)
            logger.error(f"Failed to parse exam {exam_id}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse exam: {error_msg}. Please check the exam format and ensure questions are clearly visible."
            )
        
        if not questions:
            logger.warning(f"No questions found for exam {exam_id}. Text length: {len(extracted_text)}")
            text_preview = extracted_text[:300] if len(extracted_text) > 300 else extracted_text
            error_detail = f"Failed to parse exam. No questions found.\n\n"
            error_detail += f"Text extracted: {len(extracted_text)} characters.\n\n"
            error_detail += f"Extracted text preview:\n{text_preview}\n\n"
            error_detail += "Possible issues:\n"
            error_detail += "1. The OCR extracted too little text - check image quality\n"
            error_detail += "2. The exam format is not recognized - ensure questions are clearly numbered\n"
            error_detail += "3. The text language doesn't match OCR settings\n"
            error_detail += f"4. Current OCR language: {settings.OCR_LANGUAGE}\n\n"
            error_detail += "Tips:\n"
            error_detail += "- Use a clear, high-resolution image\n"
            error_detail += "- Ensure text is readable and not too small\n"
            error_detail += "- For Hebrew text, set OCR_LANGUAGE=he in .env file\n"
            error_detail += "- Try using a .txt file if possible\n"
            error_detail += f"- Check the extracted text at: GET /api/exams/{exam_id}/text"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
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


@router.get("/{exam_id}/text")
async def get_extracted_text(exam_id: str):
    """
    Get the extracted text from an uploaded exam (for debugging).
    """
    exam = storage.get_exam(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam {exam_id} not found"
        )
    
    extracted_text = exam.get("extracted_text", "")
    return {
        "exam_id": exam_id,
        "text_length": len(extracted_text),
        "text": extracted_text,
        "preview": extracted_text[:500] if len(extracted_text) > 500 else extracted_text
    }


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


@router.get("/{exam_id}/status")
async def get_exam_status(exam_id: str):
    """
    Get the processing status of an exam.
    """
    exam = storage.get_exam(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam {exam_id} not found"
        )
    
    questions = storage.get_parsed_questions(exam_id)
    results = storage.get_results(exam_id)
    
    status_info = {
        "exam_id": exam_id,
        "uploaded": True,
        "file_type": exam.get("file_type"),
        "text_extracted": bool(exam.get("extracted_text")),
        "text_length": len(exam.get("extracted_text", "")),
        "parsed": bool(questions),
        "questions_count": len(questions) if questions else 0,
        "graded": bool(results),
        "processing_stage": "uploaded"
    }
    
    if status_info["text_extracted"]:
        status_info["processing_stage"] = "text_extracted"
    if status_info["parsed"]:
        status_info["processing_stage"] = "parsed"
    if status_info["graded"]:
        status_info["processing_stage"] = "graded"
    
    return status_info

