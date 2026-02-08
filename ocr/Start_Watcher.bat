@echo off
REM Start OCR Folder Watcher
REM Automatically processes new photos as they appear in a folder

echo ========================================
echo Journal OCR Folder Watcher
echo ========================================
echo.
echo This will monitor a folder and automatically
echo process any new journal photos you add.
echo.

REM Change to the OCR directory
cd /d "%~dp0"

REM Prompt for folder to watch
set /p WATCH_FOLDER="Enter the folder to watch (e.g., C:\Users\YourName\OneDrive\Journal Entries): "

REM Check if folder exists
if not exist "%WATCH_FOLDER%" (
    echo.
    echo Error: Folder not found: %WATCH_FOLDER%
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Folder Watcher
echo ========================================
echo.
echo Watching: %WATCH_FOLDER%
echo Output: ocr_output
echo.
echo Supported formats: .heic, .jpg, .jpeg, .png
echo (The watcher automatically detects all formats)
echo.
echo The watcher will run until you close this window.
echo Add new photos to the watch folder to process them.
echo.
echo Press Ctrl+C to stop the watcher.
echo.
pause

REM Start the watcher (it handles all file types automatically)
python auto_ocr_watcher.py "%WATCH_FOLDER%" --output "ocr_output"

echo.
echo Watcher stopped.
pause
