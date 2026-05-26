@echo off
title Vyapar Sarthi — Dev Servers
color 0A
cls

echo.
echo  ==========================================
echo   Vyapar Sarthi — Starting All Dev Servers
echo  ==========================================
echo.
echo   Landing Page  →  http://localhost:5173
echo   Frontend      →  http://localhost:3000
echo   Backend API   →  http://localhost:8000
echo   API Docs      →  http://localhost:8000/docs
echo.
echo  Press Ctrl+C to stop all servers
echo  ==========================================
echo.

:: Start Backend (FastAPI) in a new terminal window
start "Vyapar Sarthi — Backend (FastAPI :8000)" cmd /k "cd /d "%~dp0backend" && echo Starting FastAPI backend on port 8000... && uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"

:: Small delay so backend starts first
timeout /t 2 /nobreak >nul

:: Start Landing Page (Vite) in a new terminal window
start "Vyapar Sarthi — Landing Page (Vite :5173)" cmd /k "cd /d "%~dp0landing-page" && echo Starting Vite landing page on port 5173... && npm run dev"

:: Small delay
timeout /t 1 /nobreak >nul

:: Start Frontend (Next.js) in a new terminal window
start "Vyapar Sarthi — Frontend (Next.js :3000)" cmd /k "cd /d "%~dp0frontend" && echo Starting Next.js frontend on port 3000... && npm run dev"

echo.
echo  All 3 servers are starting in separate windows.
echo.
echo  Servers:
echo    Landing  →  http://localhost:5173  (opens automatically)
echo    Frontend →  http://localhost:3000
echo    Backend  →  http://localhost:8000/docs
echo.
pause
