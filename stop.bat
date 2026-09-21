@echo off
setlocal enabledelayedexpansion
title FraudShield AI - Service Shutdown

echo ============================================================
echo   FraudShield AI - Service Shutdown (Windows)
echo ============================================================
echo.

set PORTS=8000 3000 5173 8501

for %%P in (%PORTS%) do (
    echo [*] Checking port %%P...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P " 2^>nul') do (
        set PID=%%a
        if not "!PID!"=="0" (
            echo   -> Freeing port %%P (PID !PID!)...
            taskkill /f /pid !PID! >nul 2>&1
        )
    )
)

echo.
echo ============================================================
echo   [SUCCESS] FraudShield AI services have been stopped.
echo ============================================================
echo.
timeout /t 2 >nul
