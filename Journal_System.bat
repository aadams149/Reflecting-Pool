@echo off
REM Journal Processing System - Main Menu
REM Easy access to all journal processing tools

REM Anchor to this file's directory so all relative paths work
cd /d "%~dp0"

:MENU
cls
echo ========================================
echo    JOURNAL PROCESSING SYSTEM
echo ========================================
echo.
echo Select an option:
echo.
echo OCR (Digitize Photos):
echo   1. Process folder of photos
echo   2. Process single photo
echo   3. Start auto-watcher
echo.
echo RAG (Search Engine):
echo   4. Ingest journals to database
echo   5. Search journals (command line)
echo   6. Manage database (list/delete entries)
echo.
echo Dashboard (Analytics):
echo   7. Launch analytics dashboard
echo   8. Launch chat interface
echo.
echo   0. Exit
echo.
echo ========================================
echo.

set /p CHOICE="Enter your choice (0-8): "

if "%CHOICE%"=="0" goto END
if "%CHOICE%"=="1" goto OCR_FOLDER
if "%CHOICE%"=="2" goto OCR_SINGLE
if "%CHOICE%"=="3" goto WATCHER
if "%CHOICE%"=="4" goto INGEST
if "%CHOICE%"=="5" goto SEARCH
if "%CHOICE%"=="6" goto MANAGE
if "%CHOICE%"=="7" goto DASHBOARD
if "%CHOICE%"=="8" goto CHAT

echo Invalid choice. Please try again.
pause
goto MENU

:OCR_FOLDER
echo.
echo Starting OCR folder processing...
cd ocr
call Process_Photos.bat
cd ..
echo.
echo Press any key to return to main menu...
pause >nul
goto MENU

:OCR_SINGLE
echo.
echo Starting single photo processing...
cd ocr
call Process_Single_Photo.bat
cd ..
echo.
echo Press any key to return to main menu...
pause >nul
goto MENU

:WATCHER
echo.
echo Starting folder watcher...
echo.
echo Note: The watcher will run continuously until you press Ctrl+C
echo or close the window. You can return to the main menu after stopping it.
echo.
cd ocr
call Start_Watcher.bat
cd ..
echo.
echo Watcher stopped.
echo Press any key to return to main menu...
pause >nul
goto MENU

:INGEST
echo.
echo Starting RAG ingestion...
cd rag
call Ingest_Journals.bat
cd ..
echo.
echo Press any key to return to main menu...
pause >nul
goto MENU

:SEARCH
echo.
echo Starting RAG search...
cd rag
call Search_Journals.bat
cd ..
echo.
echo Press any key to return to main menu...
pause >nul
goto MENU

:MANAGE
echo.
echo Starting RAG database management...
cd rag
call Manage_Database.bat
cd ..
echo.
echo Press any key to return to main menu...
pause >nul
goto MENU

:DASHBOARD
echo.
echo Launching analytics dashboard...
start "" cmd /c "cd dashboard && Launch_Dashboard.bat"
echo.
echo Dashboard launched in new window!
echo You can keep it running and return to this menu.
echo.
timeout /t 2 >nul
goto MENU

:CHAT
echo.
echo Launching chat interface...
start "" cmd /c "cd dashboard && Launch_Chat.bat"
echo.
echo Chat interface launched in new window!
echo You can keep it running and return to this menu.
echo.
timeout /t 2 >nul
goto MENU

:END
echo.
echo Goodbye!
timeout /t 1 >nul
exit
