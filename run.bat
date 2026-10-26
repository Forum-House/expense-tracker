@echo off
setlocal enabledelayedexpansion
title Yadav ^& Yadav Daughters - Finance Tracker (Pendrive Portable)

:: Lock working directory to the pendrive / script folder
cd /d "%~dp0"

echo ==============================================================================
echo       Yadav ^& Yadav Daughters - Personal Finance Tracker (Pendrive Mode)
echo ==============================================================================
echo.

:: 1. Ensure .env exists (defaults to Auto-detecting MySQL with Portable SQLite fallback)
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Initializing default configuration from .env.example...
        copy .env.example .env >nul
    )
)

:: 2. Find Portable Python
set "PY_EXE="

:: Check 2a: Bundled Python in 'python' folder [Standard portable folder]
if exist "%~dp0python\python.exe" (
    set "PY_EXE=%~dp0python\python.exe"
    echo [INFO] Found bundled portable Python runtime [python\python.exe]
    goto :PYTHON_READY
)

:: Check 2b: Bundled Python in 'portable_python' folder
if exist "%~dp0portable_python\python.exe" (
    set "PY_EXE=%~dp0portable_python\python.exe"
    echo [INFO] Found bundled portable Python runtime [portable_python\python.exe]
    goto :PYTHON_READY
)

:: Check 2c: Working virtual environment
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_EXE=%~dp0.venv\Scripts\python.exe"
        echo [INFO] Found working virtual environment on drive.
        goto :PYTHON_READY
    )
)

:: Check 2d: Host system Python
where python >nul 2>&1
if not errorlevel 1 (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_EXE=python"
        echo [INFO] Using host system Python.
        goto :PYTHON_READY
    )
)

:: Check 2e: Host system Python Launcher [py]
where py >nul 2>&1
if not errorlevel 1 (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set "PY_EXE=py"
        echo [INFO] Using host Python Launcher [py]
        goto :PYTHON_READY
    )
)

echo [ERROR] No Python installation found.
echo Please ensure the 'python' subfolder is present in this directory.
pause
exit /b 1

:PYTHON_READY
echo.
echo ==============================================================================
echo [INFO] Ready to launch!
echo [INFO] Storage Engine: Auto (MySQL server or Portable SQLite on USB drive)
echo [INFO] Web Application: http://127.0.0.1:5000/
echo [INFO] Admin Dashboard: http://127.0.0.1:5000/admin (User: bhoomi / Pass: password)
echo [INFO] Database Studio: http://127.0.0.1:5000/db
echo ==============================================================================
echo.
echo Press Ctrl+C in this window at any time to safely shut down.
echo.

:: Automatically open browser after 2 seconds in background
start "" cmd /c "ping -n 3 127.0.0.1 >nul && start http://127.0.0.1:5000/"

:: Start application using the resolved Python executable
"%PY_EXE%" app.py

echo.
pause
