@echo off
echo Starting Backend Server with Poppler...
echo.

REM Add Poppler to PATH for this session
set PATH=%PATH%;C:\poppler-25.12.0\Library\bin

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Scripts\pip.exe" (
    echo Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
)

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with GEMINI_API_KEY
    pause
)

REM Verify Poppler is accessible
echo Checking Poppler installation...
pdftoppm -h >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Poppler not found in PATH!
    echo Make sure C:\poppler-25.12.0\Library\bin is in your system PATH
    echo Current PATH includes: %PATH%
    pause
) else (
    echo Poppler found! Starting server...
)

REM Run the server
echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

