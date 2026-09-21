@echo off
setlocal enabledelayedexpansion
title FraudShield AI - Platform Launcher

cd /d "%~dp0"

echo ============================================================
echo   FraudShield AI - One-Click Launcher (Windows)
echo ============================================================
echo.

REM 1. Activate virtual environment if available
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [NOTE] .venv not found. Using system Python. Run setup.bat first if needed.
)

REM 2. Determine mode from CLI argument
set MODE=--all
set LAUNCH_BROWSER=1

if "%1"=="--with-dashboard" set MODE=--platform
if "%1"=="--dashboard" set MODE=--platform
if "%1"=="--platform" set MODE=--platform
if "%1"=="--pipeline" (
    set MODE=--pipeline
    set LAUNCH_BROWSER=0
)
if "%1"=="--journey" (
    python run.py --journey %2
    exit /b 0
)

echo [*] Starting FraudShield AI with mode: %MODE%
echo.
echo   ----------------------------------------------------
echo   Active Services:
echo     FastAPI Backend Docs:   http://localhost:8000/docs
echo     FastAPI Health Check:   http://localhost:8000/api/health
echo     React Web Application:  http://localhost:3000/
if "%MODE%"=="--platform" (
    echo     Streamlit Dashboard:    http://localhost:8501/
)
echo   ----------------------------------------------------
echo.
echo [INFO] Opening web browser in 4 seconds...
echo Press Ctrl+C in this terminal or run stop.bat to shut down.
echo.

if %LAUNCH_BROWSER%==1 (
    start "" cmd /c "timeout /t 4 /nobreak >nul & start http://localhost:3000/"
)

python run.py %MODE%
