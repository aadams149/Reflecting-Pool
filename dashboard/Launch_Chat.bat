@echo off
REM Journal Chat Interface Launcher
REM Double-click this file to start the chat interface

echo Starting Journal Chat Interface...
echo.

REM Change to the dashboard directory
cd /d "%~dp0"

REM Launch Streamlit chat interface
python -m streamlit run journal_chat.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error launching chat. Press any key to exit.
    pause >nul
)
