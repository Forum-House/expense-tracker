#!/usr/bin/env bash
# ==============================================================================
# Yadav & Jain Company - Monthly Personal Finance Tracker Runner (Linux/macOS)
# ==============================================================================
set -e

# Change directory to the script's root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================================================="
echo "           Yadav & Jain Company - Personal Finance Tracker"
echo "=============================================================================="
echo ""

# 1. Detect Python 3
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.9+ from https://www.python.org/ or using your package manager."
    exit 1
fi

# 2. Check or create .env file from .env.example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[INFO] Creating default .env configuration file..."
    cp .env.example .env
fi

# 3. Setup Virtual Environment if missing
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    "$PYTHON_CMD" -m venv .venv
    echo "[INFO] Upgrading pip and installing requirements..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo ""
echo "[INFO] Virtual environment active: $(which python)"
echo "[INFO] Web application URL: http://127.0.0.1:5000/"
echo "[INFO] Admin Dashboard:     http://127.0.0.1:5000/admin"
echo "[INFO] Database Studio:     http://127.0.0.1:5000/db"
echo ""
echo "Press Ctrl+C to stop the server at any time."
echo ""

# Open browser in background if supported
(
    sleep 2
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://127.0.0.1:5000/" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
        open "http://127.0.0.1:5000/" >/dev/null 2>&1 || true
    fi
) &

# Run Flask backend
exec python app.py
