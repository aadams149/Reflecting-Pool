@echo off
REM OCR Processing for Journal Photos
REM Process all journal photos in a folder

echo ========================================
echo Journal OCR Processing
echo ========================================
echo.

REM Change to the OCR directory
cd /d "%~dp0"

REM Prompt for input folder
set /p INPUT_FOLDER="Enter the path to your journal photos folder: "

REM Check if folder exists
if not exist "%INPUT_FOLDER%" (
    echo.
    echo Error: Folder not found: %INPUT_FOLDER%
    echo.
    pause
    exit /b 1
)

echo.
echo Processing photos from: %INPUT_FOLDER%
echo Output will be saved to: ocr_output
echo.

REM Prompt for file format
echo What format are your photos?
echo   1. HEIC (iPhone default)
echo   2. JPG/JPEG
echo   3. PNG
echo   4. All formats (process everything)
echo.
set /p FORMAT_CHOICE="Enter choice (1-4) [default: 1]: "

if "%FORMAT_CHOICE%"=="" set FORMAT_CHOICE=1

echo.
echo Starting OCR processing...
echo.

if "%FORMAT_CHOICE%"=="1" (
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.heic" --output "ocr_output"
) else if "%FORMAT_CHOICE%"=="2" (
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.jpg" --output "ocr_output"
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.jpeg" --output "ocr_output"
) else if "%FORMAT_CHOICE%"=="3" (
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.png" --output "ocr_output"
) else if "%FORMAT_CHOICE%"=="4" (
    echo Processing HEIC files...
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.heic" --output "ocr_output"
    echo.
    echo Processing JPG files...
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.jpg" --output "ocr_output"
    echo.
    echo Processing JPEG files...
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.jpeg" --output "ocr_output"
    echo.
    echo Processing PNG files...
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.png" --output "ocr_output"
) else (
    echo Invalid choice. Defaulting to HEIC...
    python journal_ocr.py "%INPUT_FOLDER%" --pattern "*.heic" --output "ocr_output"
)

echo.
echo ========================================
echo OCR Processing Complete!
echo ========================================
echo.
echo Check the 'ocr_output' folder for results.
echo.
pause
