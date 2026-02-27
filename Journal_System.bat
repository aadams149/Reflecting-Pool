@echo off
REM Reflecting Pool - Main Menu
REM Central launcher for all journal processing tools

REM Anchor to this file's directory so all relative paths work
cd /d "%~dp0"

:MENU
cls
echo ========================================
echo        REFLECTING POOL
echo ========================================
echo.
echo Select an option:
echo.
echo App:
echo   1. Launch Reflecting Pool (recommended)
echo.
echo OCR (Digitize Photos):
echo   2. Process folder of photos
echo   3. Process single photo
echo   4. Start auto-watcher
echo.
echo RAG (Search Engine):
echo   5. Ingest journals to database
echo   6. Search journals (command line)
echo   7. Manage database (list/delete entries)
echo.
echo Legacy (standalone views):
echo   8. Launch analytics dashboard only
echo   9. Launch chat interface only
echo.
echo   0. Exit
echo.
echo ========================================
echo.

set /p CHOICE="Enter your choice (0-9): "

if "%CHOICE%"=="0" goto END
if "%CHOICE%"=="1" goto APP
if "%CHOICE%"=="2" goto OCR_FOLDER
if "%CHOICE%"=="3" goto OCR_SINGLE
if "%CHOICE%"=="4" goto WATCHER
if "%CHOICE%"=="5" goto INGEST
if "%CHOICE%"=="6" goto SEARCH
if "%CHOICE%"=="7" goto MANAGE
if "%CHOICE%"=="8" goto DASHBOARD
if "%CHOICE%"=="9" goto CHAT

echo Invalid choice. Please try again.
pause
goto MENU

:APP
echo.
echo Launching Reflecting Pool...
start "" /min cmd /c "python -m streamlit run app.py"
echo.
echo App launched in new window!
echo You can keep it running and return to this menu.
echo.
timeout /t 2 >nul
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
