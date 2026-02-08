@echo off
REM Journal Dashboard Launcher
REM Double-click this file to start the dashboard

echo Starting Journal Dashboard...
echo.

REM Change to the dashboard directory
cd /d "%~dp0"

REM Launch Streamlit dashboard
python -m streamlit run journal_dashboard.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error launching dashboard. Press any key to exit.
    pause >nul
)
