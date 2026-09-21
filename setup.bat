@echo off
setlocal enabledelayedexpansion
title FraudShield AI - Environment Setup

echo ============================================================
echo   FraudShield AI - One-Click Environment Setup (Windows)
echo ============================================================
echo.

cd /d "%~dp0"

REM 1. Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not available on PATH.
    echo Please install Python 3.10 or higher from https://python.org and tick "Add python.exe to PATH".
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] Found %%i

REM 2. Check Node.js and npm
echo.
echo [*] Checking Node.js and npm...
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Node.js is not installed or not available on PATH.
    echo Frontend build requires Node.js 18+. You can install from https://nodejs.org/
) else (
    for /f "tokens=*" %%i in ('node --version') do echo [OK] Found Node %%i
)

REM 3. Virtual Environment Setup
echo.
echo [*] Setting up Python virtual environment (.venv)...
if not exist ".venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment in .venv...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Existing virtual environment found.
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM 4. Upgrade pip and install Python dependencies
echo.
echo [*] Installing Python requirements...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)
echo [OK] Python dependencies installed successfully.

REM 5. Frontend dependencies
if exist "frontend\package.json" (
    echo.
    echo [*] Installing frontend npm packages...
    pushd frontend
    call npm install
    popd
    echo [OK] Frontend packages installed.
)

REM 6. Environment configuration file
echo.
if not exist ".env" (
    echo [*] Generating .env from .env.example...
    copy ".env.example" ".env" >nul
    echo [OK] Created .env configuration file.
) else (
    echo [OK] Existing .env file detected.
)

REM 7. Ensure necessary runtime directories exist
echo.
echo [*] Ensuring runtime directories exist...
if not exist "logs" mkdir logs
if not exist "data\raw" mkdir "data\raw"
if not exist "data\relational" mkdir "data\relational"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\features" mkdir "data\features"
if not exist "data\graph" mkdir "data\graph"
if not exist "reports" mkdir reports
echo [OK] Runtime directories verified.

REM 8. Run system health check
echo.
echo [*] Executing health diagnostics...
python scripts\health_check.py
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Health check reported warnings. Review output above.
)

echo.
echo ============================================================
echo   [SUCCESS] FraudShield AI is fully set up and ready!
echo.
echo   To start the platform, run:
echo       run.bat
echo   To run automated tests, run:
echo       test.bat
echo   To stop all services, run:
echo       stop.bat
echo ============================================================
echo.
pause
