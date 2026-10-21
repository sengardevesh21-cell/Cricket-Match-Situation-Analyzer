@echo off
title Cricket Match Situation Analyzer
echo ==========================================================
echo       CRICKET MATCH SITUATION ANALYZER - BCA PROJECT
echo ==========================================================
echo.

:: Check if Python is available in PATH
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.8+ and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment in .venv ...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
)

:: Install / verify dependencies
echo [INFO] Verifying project dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Dependency verification had warnings, attempting to launch...
)

echo.
echo ==========================================================
echo Launching Application at: http://127.0.0.1:5000/
echo Press Ctrl+C in this terminal window to stop the server.
echo ==========================================================
echo.

:: Automatically open default web browser
start "" "http://127.0.0.1:5000/"

:: Start Flask server
".venv\Scripts\python.exe" app.py

pause
