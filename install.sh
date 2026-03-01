#!/usr/bin/env bash
# Reflecting Pool - Installation Script (macOS / Linux)
# Checks prerequisites, installs dependencies, and sets up the project.
set -e

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC} $1"; }
warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
fail() { echo -e "  ${RED}[X]${NC} $1"; }

echo "========================================"
echo "  Reflecting Pool - Setup"
echo "========================================"
echo

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Darwin) PLATFORM="macos" ;;
    Linux)  PLATFORM="linux" ;;
    *)      PLATFORM="other" ;;
esac

# ---- Step 1: Python ----
echo "[1/5] Checking Python..."
if command -v python3 &>/dev/null; then
    PY=$(python3 --version 2>&1)
    ok "Found $PY"
elif command -v python &>/dev/null; then
    PY=$(python --version 2>&1)
    ok "Found $PY"
else
    fail "Python is not installed."
    if [ "$PLATFORM" = "macos" ]; then
        echo "       Install with: brew install python"
    elif [ "$PLATFORM" = "linux" ]; then
        echo "       Install with: sudo apt install python3 python3-pip"
    fi
    exit 1
fi

# ---- Step 2: Tesseract ----
echo
echo "[2/5] Checking Tesseract OCR..."
if command -v tesseract &>/dev/null; then
    TV=$(tesseract --version 2>&1 | head -1)
    ok "Found $TV"
else
    warn "Tesseract OCR not found. OCR features will not work."
    if [ "$PLATFORM" = "macos" ]; then
        echo "       Install with: brew install tesseract"
    elif [ "$PLATFORM" = "linux" ]; then
        echo "       Install with: sudo apt-get install tesseract-ocr"
    fi
    echo
    read -rp "  Continue without Tesseract? (y/n): " CONT
    if [ "$CONT" != "y" ] && [ "$CONT" != "Y" ]; then
        exit 1
    fi
fi

# ---- Step 3: pip dependencies ----
echo
echo "[3/5] Installing Python dependencies..."
echo "  This may take a few minutes on the first run."
echo
python3 -m pip install --upgrade pip 2>/dev/null || true
python3 -m pip install -r requirements.txt
ok "Dependencies installed."

# ---- Step 4: Ollama ----
echo
echo "[4/5] Checking Ollama (optional, for AI chat)..."
if command -v ollama &>/dev/null; then
    ok "Found Ollama"
    echo "       Tip: run 'ollama pull mistral' if you haven't already."
else
    warn "Ollama not found. AI chat will use search-only mode."
    echo "       To enable AI answers later, install from: https://ollama.ai"
fi

# ---- Step 5: Launch script ----
echo
echo "[5/5] Setting up launch script..."
if [ -f "launch.sh" ]; then
    chmod +x launch.sh
    ok "launch.sh is ready."
else
    warn "launch.sh not found."
fi

# ---- Done ----
echo
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo
echo "  To launch the app:"
echo "    ./launch.sh"
echo "    Or: python3 -m streamlit run app.py"
echo
echo "  First time? Process some journal photos with the OCR"
echo "  pipeline, then ingest them from the sidebar."
echo
