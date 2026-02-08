@echo off
REM Ingest Journal Entries into RAG Database
REM Processes OCR output and adds to vector database for searching

echo ========================================
echo RAG Database Ingestion
echo ========================================
echo.
echo This will load your journal entries into
echo the RAG database for semantic search.
echo.

REM Change to the RAG directory
cd /d "%~dp0"

REM Default paths
set OCR_OUTPUT=..\ocr\ocr_output
set RAG_DB=vector_db

echo Using default paths:
echo   OCR Output: %OCR_OUTPUT%
echo   RAG Database: %RAG_DB%
echo.

REM Check if OCR output exists
if not exist "%OCR_OUTPUT%\text" (
    echo.
    echo Error: OCR output not found at %OCR_OUTPUT%
    echo.
    echo Please run OCR processing first:
    echo   1. Go to the 'ocr' folder
    echo   2. Run Process_Photos.bat or Process_Single_Photo.bat
    echo   3. Then come back here and run this again
    echo.
    pause
    exit /b 1
)

echo Press any key to start ingestion...
pause >nul

echo.
echo ========================================
echo Starting Ingestion...
echo ========================================
echo.

REM Run ingestion
python journal_rag.py ingest "%OCR_OUTPUT%" --db "%RAG_DB%"

echo.
echo ========================================
echo Ingestion Complete!
echo ========================================
echo.
echo Your journal entries are now searchable!
echo.
echo To search:
echo   - Use the chat interface (Launch_Chat.bat in dashboard folder)
echo   - Or run: python journal_rag.py interactive
echo.
pause
