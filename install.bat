@echo off
REM Reflecting Pool - Installation Wizard
REM Checks prerequisites, installs dependencies, and optionally builds the desktop launcher.

cd /d "%~dp0"

echo ========================================
echo   Reflecting Pool - Setup Wizard
echo ========================================
echo.

REM ------------------------------------------------------------------
REM Step 1: Python
REM ------------------------------------------------------------------
echo [1/5] Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   ERROR: Python is not installed or not on your PATH.
    echo   Download it from https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo   Found %%v

REM ------------------------------------------------------------------
REM Step 2: Tesseract OCR
REM ------------------------------------------------------------------
echo.
echo [2/5] Checking Tesseract OCR...
where tesseract >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo   Found Tesseract at C:\Program Files\Tesseract-OCR\tesseract.exe
    ) else (
        echo   WARNING: Tesseract OCR not found.
        echo   OCR features will not work without it.
        echo   Download from: https://github.com/UB-Mannheim/tesseract/wiki
        echo   Install to the default location: C:\Program Files\Tesseract-OCR
        echo.
        set /p CONT="Continue without Tesseract? (y/n): "
        if /i not "%CONT%"=="y" exit /b 1
    )
) else (
    echo   Found Tesseract on PATH
)

REM ------------------------------------------------------------------
REM Step 3: pip dependencies
REM ------------------------------------------------------------------
echo.
echo [3/5] Installing Python dependencies...
echo   This may take a few minutes on the first run.
echo.
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo   ERROR: pip install failed. Check the output above for details.
    pause
    exit /b 1
)
echo.
echo   Dependencies installed successfully.

REM ------------------------------------------------------------------
REM Step 4: Ollama (optional)
REM ------------------------------------------------------------------
echo.
echo [4/5] Checking Ollama (optional, for AI chat)...
where ollama >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   Ollama not found. AI chat will use search-only mode.
    echo   To enable AI answers later, install from: https://ollama.ai
    echo   Then run: ollama pull mistral
) else (
    echo   Found Ollama on PATH
    echo   Tip: run "ollama pull mistral" if you haven't already.
)

REM ------------------------------------------------------------------
REM Step 5: Desktop launcher (optional)
REM ------------------------------------------------------------------
echo.
echo [5/5] Build desktop launcher (.exe)?
echo   This creates a native desktop app (~14 MB).
echo   You can always launch via "python -m streamlit run app.py" instead.
echo.
set /p BUILD="Build the .exe? (y/n): "
if /i "%BUILD%"=="y" (
    echo.
    echo   Installing build tools...
    python -m pip install pyinstaller >nul 2>&1
    echo   Building Reflecting Pool.exe...
    python -m PyInstaller --onefile --noconsole --name "Reflecting Pool" --icon favicon.ico launcher.py >nul 2>&1
    if exist "dist\Reflecting Pool.exe" (
        move /y "dist\Reflecting Pool.exe" "Reflecting Pool.exe" >nul
        echo   Built successfully: Reflecting Pool.exe
    ) else (
        echo   Build failed. You can still run the app with:
        echo     python -m streamlit run app.py
    )
)

REM ------------------------------------------------------------------
REM Done
REM ------------------------------------------------------------------
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo   To launch the app:
if exist "Reflecting Pool.exe" (
    echo     - Double-click "Reflecting Pool.exe"
)
echo     - Double-click Journal_System.bat and press 1
echo     - Or run: python -m streamlit run app.py
echo.
echo   First time? Process some journal photos with the OCR
echo   pipeline, then ingest them from the sidebar.
echo.
pause
