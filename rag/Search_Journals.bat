@echo off
REM Interactive RAG Search
REM Search your journals from the command line

echo ========================================
echo Journal RAG Search Interface
echo ========================================
echo.

REM Change to the RAG directory
cd /d "%~dp0"

REM Check if database exists
if not exist "vector_db" (
    echo.
    echo Error: RAG database not found!
    echo.
    echo Please run Ingest_Journals.bat first to create the database.
    echo.
    pause
    exit /b 1
)

echo Starting interactive search...
echo.
echo Available commands:
echo   search ^<query^>  - Search your journals
echo   dates            - List all entry dates
echo   stats            - Show database statistics
echo   quit             - Exit
echo.
echo You can also use the chat interface for a better experience!
echo (Run Launch_Chat.bat in the dashboard folder)
echo.
pause

REM Start interactive search
python journal_rag.py interactive --db "vector_db"

pause
