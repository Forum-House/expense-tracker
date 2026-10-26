#!/usr/bin/env bash
# ==============================================================================
# Yadav & Jain Company - Environment Setup (Linux/macOS)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================================================="
echo "          Yadav & Jain Company - Environment Setup (Linux/macOS)"
echo "=============================================================================="
echo ""

PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python is not installed."
    exit 1
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[INFO] Creating default .env configuration file..."
    cp .env.example .env
fi

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    "$PYTHON_CMD" -m venv .venv
fi

source .venv/bin/activate
echo "[INFO] Upgrading pip..."
pip install --upgrade pip

echo "[INFO] Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "=============================================================================="
echo "Setup completed successfully! Run the app using ./run.sh"
echo "=============================================================================="
echo ""
