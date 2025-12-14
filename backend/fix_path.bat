@echo off
echo Adding Poppler to PATH...

REM Add to current session
set PATH=%PATH%;C:\poppler-25.12.0\Library\bin

REM Add permanently to user PATH
setx PATH "%PATH%;C:\poppler-25.12.0\Library\bin"

echo Testing Poppler...
pdftoppm -h

echo.
echo PATH updated! Restart your terminal and try again.
pause