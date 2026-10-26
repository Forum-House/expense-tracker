@echo off
setlocal enabledelayedexpansion
title Yadav ^& Yadav Daughters - Setup Environment

echo ==============================================================================
echo            Yadav ^& Yadav Daughters - Environment Setup (Windows)
echo ==============================================================================
echo.

:: Check if portable python is already bundled
if exist "%~dp0python\python.exe" (
    echo [INFO] Bundled portable Python is already configured and ready to use!
    echo [INFO] No system Python installation is required.
    echo [INFO] You can launch the app immediately using start.bat or run.bat.
    echo.
    pause
    exit /b 0
)

if exist "%~dp0portable_python\python.exe" (
    echo [INFO] Bundled portable Python is already configured and ready to use!
    echo [INFO] No system Python installation is required.
    echo [INFO] You can launch the app immediately using start.bat or run.bat.
    echo.
    pause
    exit /b 0
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.9+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Creating .env from .env.example...
        copy .env.example .env >nul
    )
)

if exist ".venv" (
    echo [INFO] Existing .venv found. Activating...
) else (
    echo [INFO] Creating virtual environment (.venv)...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing requirements from requirements.txt...
pip install -r requirements.txt

echo.
echo ==============================================================================
echo Setup completed successfully! You can now run the app using run.bat
echo ==============================================================================
echo.
pause
