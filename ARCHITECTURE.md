# System Architecture

## Overview
AI-powered exam grading system with OCR and Gemini API integration.

## Architecture Diagram

```
┌─────────────────┐
│   React Frontend │
│   (Port 3000)    │
└────────┬─────────┘
         │ HTTP/REST
         │
┌────────▼─────────┐
│  FastAPI Backend │
│   (Port 8000)    │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ OCR   │ │ Gemini│
│Engine │ │  API  │
└───────┘ └───────┘
```

## Components

### Frontend (React)
- **Purpose**: User interface for exam upload and results visualization
- **Technology**: React 18+ with modern hooks
- **Features**:
  - File upload (PDF/image/text)
  - Student answer submission
  - Results dashboard with per-question breakdown
  - Final grade display

### Backend (FastAPI)
- **Purpose**: API server handling OCR, AI processing, and grading logic
- **Technology**: Python 3.11+, FastAPI, Uvicorn
- **Key Modules**:
  - `ocr_service.py`: OCR extraction using EasyOCR/Tesseract
  - `gemini_service.py`: Gemini API integration
  - `grading_service.py`: Business logic for grading
  - `models.py`: Pydantic models for request/response
- **Endpoints**:
  - `POST /api/exams/upload`: Upload solved exam
  - `POST /api/exams/{exam_id}/parse`: Parse exam into questions
  - `POST /api/exams/{exam_id}/grade`: Grade student answers
  - `GET /api/exams/{exam_id}/results`: Get grading results

### OCR Service
- **Library**: EasyOCR (primary) or Tesseract (fallback)
- **Input**: PDF, images (PNG, JPG), text files
- **Output**: Cleaned text string

### Gemini API Integration
- **Model**: Gemini Pro or Gemini 1.5
- **Two Prompts**:
  1. **Exam Parsing**: Extract structured Q&A from OCR text
  2. **Answer Grading**: Compare student answer to correct answer

### Data Flow

1. **Exam Upload Flow**:
   ```
   User → Frontend → Backend → OCR → Text → Gemini (Parse) → Structured Q&A → Storage
   ```

2. **Grading Flow**:
   ```
   User → Frontend → Backend → Gemini (Grade) → Scores → Aggregation → Results → Frontend
   ```

## Security

- API keys stored in environment variables (backend only)
- Input validation on all endpoints
- File type and size restrictions
- CORS configuration for frontend-backend communication

## Storage

- In-memory storage (can be extended to database)
- Exam data stored temporarily during session
- Results cached for retrieval

## Error Handling

- Graceful OCR failures with retry logic
- Gemini API rate limiting and retries
- User-friendly error messages
- Comprehensive logging

