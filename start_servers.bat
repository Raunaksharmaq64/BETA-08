@echo off
title RIGHT FIT — All Servers Launcher
color 0A
echo ==============================================================================
echo                      RIGHT FIT - SERVER LAUNCHER
echo ==============================================================================
echo.
echo [1/2] Starting Core FastAPI Backend on http://localhost:8000 ...
start "RIGHT FIT Core Backend (FastAPI :8000)" cmd /k "cd /d "%~dp0" && python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
start "RIGHT FIT Frontend (Next.js :3000)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ==============================================================================
echo Servers successfully launched in dedicated windows!
echo - Core Backend API:   http://localhost:8000
echo - Swagger API Docs:   http://localhost:8000/docs
echo - Health Check Live:  http://localhost:8000/health/live
echo - Next.js Frontend:   http://localhost:3000
echo ==============================================================================
echo.
pause
