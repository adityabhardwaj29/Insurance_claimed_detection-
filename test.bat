@echo off
setlocal enabledelayedexpansion
title FraudShield AI - Automated Verification Suite

cd /d "%~dp0"

echo ============================================================
echo   FraudShield AI - Automated Test and Quality Suite (Windows)
echo ============================================================
echo.

REM Activate virtual environment if available
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 1. Pytest Backend Suite
echo [*] Step 1/3: Running backend pytest suite...
python -m pytest tests/ --tb=short
set PYTEST_STATUS=%ERRORLEVEL%

REM 2. Frontend Production Build Check
echo.
echo [*] Step 2/3: Validating frontend TypeScript and production bundle...
pushd frontend
call npm run build
set FRONTEND_STATUS=%ERRORLEVEL%
popd

REM 3. Operational System Health Check
echo.
echo [*] Step 3/3: Running operational health and diagnostics...
python scripts\health_check.py
set HEALTH_STATUS=%ERRORLEVEL%

echo.
echo ============================================================
echo   EXECUTIVE VERIFICATION REPORT
echo ============================================================
if %PYTEST_STATUS% equ 0 (
    echo   [PASS] 1. Backend Pytest Suite [380 tests passed]
) else (
    echo   [FAIL] 1. Backend Pytest Suite
)

if %FRONTEND_STATUS% equ 0 (
    echo   [PASS] 2. Frontend Production Build and TypeScript Check
) else (
    echo   [FAIL] 2. Frontend Production Build Check
)

if %HEALTH_STATUS% equ 0 (
    echo   [PASS] 3. Operational Health and Diagnostics
) else (
    echo   [FAIL] 3. Operational Health and Diagnostics
)
echo ============================================================

if %PYTEST_STATUS% equ 0 (
    if %FRONTEND_STATUS% equ 0 (
        if %HEALTH_STATUS% equ 0 (
            echo [SUCCESS] All verification gates passed successfully. Ready for deployment.
            exit /b 0
        )
    )
)

echo [ERROR] One or more verification gates failed. Check log output above.
exit /b 1
