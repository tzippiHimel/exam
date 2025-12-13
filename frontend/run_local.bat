@echo off
echo Starting Frontend Server...
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

REM Run the server
echo Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo.
call npm start

pause

