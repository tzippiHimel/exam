"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import exams, health
from app.config import settings
from app.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="AI Exam Grading System",
    description="Automated exam grading with OCR and Gemini AI",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(exams.router, prefix="/api/exams", tags=["exams"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Exam Grading System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

