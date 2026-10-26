@echo off
setlocal enabledelayedexpansion
title Yadav ^& Yadav Daughters - Personal Finance Tracker (Portable)
color 0B

cd /d "%~dp0"

echo ==============================================================================
echo       Yadav ^& Yadav Daughters - Personal Finance Tracker (Portable)
echo ==============================================================================
echo.

:: Detect Python executable (Bundled portable Python runtime takes priority)
set "PY_EXE="

if exist "%~dp0python\python.exe" (
    set "PY_EXE=%~dp0python\python.exe"
    echo [*] Found bundled portable Python runtime [python\python.exe]
    goto :PYTHON_FOUND
)

if exist "%~dp0portable_python\python.exe" (
    set "PY_EXE=%~dp0portable_python\python.exe"
    echo [*] Found bundled portable Python runtime [portable_python\python.exe]
    goto :PYTHON_FOUND
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_EXE=python"
        echo [*] Using host system Python.
        goto :PYTHON_FOUND
    )
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_EXE=py"
        echo [*] Using host Python Launcher [py]
        goto :PYTHON_FOUND
    )
)

:PYTHON_FOUND
if "%PY_EXE%"=="" (
    color 0C
    echo [ERROR] No Python runtime found!
    echo Please make sure the 'python' subfolder is present in this directory.
    echo.
    pause
    exit /b 1
)

:: Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
    )
)

echo [*] Initializing database and starting server...
echo [*] Web Application: http://127.0.0.1:5000/
echo [*] Admin Dashboard: http://127.0.0.1:5000/admin [User: bhoomi / Pass: password]
echo [*] Database Studio: http://127.0.0.1:5000/db
echo.
echo Opening web browser in 2 seconds...
echo [Keep this command window open while using the application]
echo.

:: Open default browser after 2 seconds in background
start "" cmd /c "ping -n 3 127.0.0.1 >nul && start http://127.0.0.1:5000/"

:: Launch the Flask app
"%PY_EXE%" app.py

echo.
echo Application stopped.
pause
