# AI-Powered Exam Grading System

A production-level web application that automatically grades exams using OCR and Google's Gemini AI.

## 🎯 Features

- **OCR Text Extraction**: Extracts text from PDF, images, and text files using EasyOCR
- **AI-Powered Parsing**: Uses Gemini AI to parse exam documents into structured questions and answers
- **Intelligent Grading**: Automatically grades student answers with detailed explanations
- **Modern UI**: Clean, responsive React frontend with step-by-step workflow
- **Dockerized**: Fully containerized with Docker Compose for easy deployment
- **Tested**: Comprehensive unit and integration tests

## 🏗️ Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system architecture.

### Tech Stack

**Frontend:**
- React 18
- Modern CSS with responsive design

**Backend:**
- FastAPI (Python 3.11+)
- EasyOCR for text extraction
- Google Gemini API for AI processing
- Pydantic for data validation

**Infrastructure:**
- Docker & Docker Compose
- GitHub Actions for CI/CD

## 📋 Prerequisites

- Docker and Docker Compose installed
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd exam
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
OCR_LANGUAGE=en
MAX_FILE_SIZE_MB=10
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build the backend and frontend Docker images
- Start both services
- Backend available at: http://localhost:8000
- Frontend available at: http://localhost:3000
- API docs at: http://localhost:8000/docs

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## 📖 Usage Guide

### Step 1: Upload Solved Exam
1. Click "Browse" and select a solved exam file (PDF, image, or text)
2. The exam should contain questions and their correct answers
3. Click "Upload Exam"

### Step 2: Parse Exam
1. After upload, click "Parse Exam"
2. The system will extract text using OCR and parse it into questions using AI
3. Review the parsed questions

### Step 3: Submit Student Answers
1. Enter the student's answers for each question
2. Click "Submit Answers for Grading"
3. The system will grade each answer using AI

### Step 4: View Results
1. See the final score and grade
2. Review per-question results with explanations
3. Click "Grade Another Exam" to start over

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=html
```

### Integration Tests

```bash
docker-compose up -d
pytest backend/tests/test_integration.py
```

## 📁 Project Structure

```
exam/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Pydantic models
│   │   ├── routers/             # API routes
│   │   │   ├── exams.py        # Exam endpoints
│   │   │   └── health.py       # Health check
│   │   └── services/           # Business logic
│   │       ├── ocr_service.py  # OCR extraction
│   │       ├── gemini_service.py # AI integration
│   │       ├── grading_service.py # Grading logic
│   │       └── storage.py      # Data storage
│   ├── tests/                   # Test files
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main app component
│   │   ├── components/         # React components
│   │   │   ├── ExamUpload.js
│   │   │   ├── StudentAnswers.js
│   │   │   └── ResultsDashboard.js
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .github/workflows/ci.yml
├── ARCHITECTURE.md
└── README.md
```

## 🔌 API Endpoints

### Upload Exam
```http
POST /api/exams/upload
Content-Type: multipart/form-data

Body: file (PDF, image, or text)
```

### Parse Exam
```http
POST /api/exams/{exam_id}/parse
```

### Grade Answers
```http
POST /api/exams/{exam_id}/grade
Content-Type: application/json

{
  "exam_id": "uuid",
  "student_answers": [
    {
      "question_index": 0,
      "answer": "Student's answer"
    }
  ]
}
```

### Get Results
```http
GET /api/exams/{exam_id}/results
```

See full API documentation at http://localhost:8000/docs

## 🔒 Security

- API keys stored in environment variables (never in code)
- Input validation on all endpoints
- File type and size restrictions
- CORS configuration for frontend-backend communication

## 🐛 Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed in the Docker container
- Check that images are clear and readable
- Verify file format is supported

### Gemini API Errors
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota and rate limits
- Ensure internet connectivity

### Docker Issues
- Ensure Docker and Docker Compose are installed
- Check ports 3000 and 8000 are not in use
- Review Docker logs: `docker-compose logs`

## 📝 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is for academic purposes.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- EasyOCR for text extraction
- FastAPI and React communities

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This is a production-level academic project. Ensure you have proper API keys and follow best practices for deployment.

