@echo off
echo Installing Poppler for PDF processing...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - Good!
) else (
    echo This script should be run as administrator for best results.
    echo Right-click and select "Run as administrator"
    echo.
    pause
)

echo Step 1: Creating poppler directory...
if not exist "C:\poppler" (
    mkdir "C:\poppler"
    echo Created C:\poppler directory
) else (
    echo C:\poppler directory already exists
)

echo.
echo Step 2: Download Poppler manually:
echo 1. Go to: https://github.com/oschwartz10612/poppler-windows/releases/latest
echo 2. Download "Release-XX.XX.X-0.zip" (latest version)
echo 3. Extract the contents to C:\poppler
echo 4. Make sure you have C:\poppler\Library\bin folder
echo.

echo Step 3: Adding to PATH...
REM Add to system PATH
setx PATH "%PATH%;C:\poppler\Library\bin" /M >nul 2>&1
if %errorLevel% == 0 (
    echo Added C:\poppler\Library\bin to system PATH
) else (
    echo Failed to add to system PATH, trying user PATH...
    setx PATH "%PATH%;C:\poppler\Library\bin" >nul 2>&1
    if %errorLevel% == 0 (
        echo Added C:\poppler\Library\bin to user PATH
    ) else (
        echo Failed to add to PATH automatically.
        echo Please add C:\poppler\Library\bin to your PATH manually:
        echo 1. Open System Properties ^> Environment Variables
        echo 2. Edit PATH variable
        echo 3. Add: C:\poppler\Library\bin
    )
)

echo.
echo Step 4: Testing installation...
echo Checking if poppler is in PATH...

REM Test if pdftoppm is available
pdftoppm -h >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Poppler is working correctly!
) else (
    echo ✗ Poppler not found in PATH
    echo Make sure you:
    echo 1. Downloaded and extracted poppler to C:\poppler
    echo 2. Restarted your terminal/IDE
    echo 3. The path C:\poppler\Library\bin exists
)

echo.
echo Installation complete!
echo Please restart your IDE/terminal and try uploading PDF again.
echo.
pause