@echo off
REM Rex Cursor Desktop App Launcher
REM Starts both server and Electron app

echo.
echo ================================================
echo   REX CURSOR DESKTOP APP LAUNCHER
echo ================================================
echo.
echo Starting components...
echo.

REM Get current directory
cd /d "%~dp0"

REM Check if rex-cursor-app exists
if not exist "rex-cursor-app\package.json" (
    echo ERROR: Rex Cursor App not found!
    echo Please run installation first.
    echo.
    pause
    exit /b 1
)

REM Start Rex Enhanced Server
echo [1/2] Starting Rex Server with auto-rotation...
start "Rex Enhanced Server" cmd /k python rex_server_enhanced.py 8000

REM Wait for server to initialize
echo [2/2] Waiting for server to start...
timeout /t 8 /nobreak > nul

REM Start Electron app
echo [2/2] Launching Rex Cursor Desktop App...
cd rex-cursor-app
start "Rex Cursor App" cmd /k npm run dev

echo.
echo ================================================
echo   BOTH COMPONENTS LAUNCHED!
echo ================================================
echo.
echo Server: Port 8000 (watch for auto-rotations)
echo Desktop App: Electron window will open
echo.
echo You can close this launcher window now.
echo The server and app will keep running.
echo.
pause
