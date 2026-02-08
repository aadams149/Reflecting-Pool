@echo off
REM OCR Single Photo
REM Process one journal photo at a time

echo ========================================
echo Process Single Journal Photo
echo ========================================
echo.

REM Change to the OCR directory
cd /d "%~dp0"

REM Prompt for photo path
set /p PHOTO_PATH="Enter the full path to your photo: "

REM Check if file exists
if not exist "%PHOTO_PATH%" (
    echo.
    echo Error: File not found: %PHOTO_PATH%
    echo.
    pause
    exit /b 1
)

REM Prompt for date (optional)
set /p ENTRY_DATE="Enter entry date (YYYY-MM-DD) or press Enter to use filename: "

echo.
echo Processing: %PHOTO_PATH%
echo.

REM Run OCR
if "%ENTRY_DATE%"=="" (
    python journal_ocr.py "%PHOTO_PATH%" --output "ocr_output"
) else (
    python journal_ocr.py "%PHOTO_PATH%" --date "%ENTRY_DATE%" --output "ocr_output"
)

echo.
echo ========================================
echo Processing Complete!
echo ========================================
echo.
echo Check the 'ocr_output' folder for results.
echo.
pause
