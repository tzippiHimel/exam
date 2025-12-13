@echo off
echo ========================================
echo   AI Exam Grading System - Local Run
echo ========================================
echo.

echo This will start both Backend and Frontend
echo Make sure you have:
echo   1. Python 3.11+ installed
echo   2. Node.js 18+ installed
echo   3. Tesseract OCR installed
echo   4. .env file in backend/ with GEMINI_API_KEY
echo.
pause

echo Starting Backend...
start "Backend Server" cmd /k "cd backend && run_local.bat"

timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Frontend Server" cmd /k "cd frontend && run_local.bat"

echo.
echo ========================================
echo   Servers are starting...
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit (servers will keep running)
pause >nul

