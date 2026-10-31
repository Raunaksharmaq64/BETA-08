@echo off
title RIGHT FIT — All Servers Launcher
color 0A
echo ==============================================================================
echo                      RIGHT FIT - SERVER LAUNCHER
echo ==============================================================================
echo.

echo Cleaning lingering processes on ports 8000, 8002, 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo Freeing port 8000 (PID %%a)...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002 " ^| findstr "LISTENING"') do (
    echo Freeing port 8002 (PID %%a)...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    echo Freeing port 3000 (PID %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [1/3] Starting Core FastAPI Backend on http://localhost:8000 ...
start "RIGHT FIT Core Backend (FastAPI :8000)" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/3] Starting Startup Intelligence Satellite on http://localhost:8002 ...
start "Startup Intelligence Service (FastAPI :8002)" cmd /k "cd /d %~dp0..\Startups-problrms-hunter && python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload"

timeout /t 2 /nobreak >nul

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "RIGHT FIT Frontend (Next.js :3000)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ==============================================================================
echo Servers successfully launched in dedicated windows!
echo - Core Backend API:        http://localhost:8000
echo - Swagger API Docs:        http://localhost:8000/docs
echo - Health Check Live:       http://localhost:8000/health/live
echo - Startup Intelligence:    http://localhost:8002
echo - Startup Health Live:     http://localhost:8002/health
echo - Next.js Frontend:        http://localhost:3000
echo ==============================================================================
echo.
pause
