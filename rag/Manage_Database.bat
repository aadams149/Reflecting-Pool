@echo off
REM Manage RAG Database Entries
REM List, delete, or clear journal entries from the RAG database

echo ========================================
echo RAG Database Management
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

:MENU
cls
echo ========================================
echo RAG Database Management
echo ========================================
echo.
echo What would you like to do?
echo.
echo   1. List all entries
echo   2. Delete entry by date
echo   3. Clear entire database
echo   4. Show database statistics
echo   0. Exit
echo.
echo ========================================
echo.

set /p CHOICE="Enter your choice (0-4): "

if "%CHOICE%"=="0" goto END
if "%CHOICE%"=="1" goto LIST
if "%CHOICE%"=="2" goto DELETE
if "%CHOICE%"=="3" goto CLEAR
if "%CHOICE%"=="4" goto STATS

echo Invalid choice. Please try again.
pause
goto MENU

:LIST
echo.
echo Listing all entries in database...
echo.
python journal_rag.py list --db "vector_db"
echo.
pause
goto MENU

:DELETE
echo.
set /p DELETE_DATE="Enter the date to delete (YYYY-MM-DD): "
echo.
python journal_rag.py delete "%DELETE_DATE%" --db "vector_db"
echo.
pause
goto MENU

:CLEAR
echo.
echo ========================================
echo WARNING: This will delete ALL entries!
echo ========================================
echo.
python journal_rag.py clear --db "vector_db"
echo.
pause
goto MENU

:STATS
echo.
python journal_rag.py stats --db "vector_db"
echo.
pause
goto MENU

:END
echo.
echo Goodbye!
timeout /t 1 >nul
exit
