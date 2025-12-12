@echo off
cls
echo ========================================
echo   ROVODEV AUTO - FULL STACK LAUNCHER
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Set MCP config
set ROVODEV_MCP_CONFIG=%SCRIPT_DIR%mcp_testing_config.json

echo [1/3] Starting Ollama...
start /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✅ Ollama started
echo.

echo [2/3] Starting MCP Testing Server...
start "MCP Testing Server" /MIN cmd /c "cd /d %SCRIPT_DIR%mcp_testing_server && python server.py"
timeout /t 2 /nobreak >nul
echo       ✅ MCP Server started (running in background)
echo.

echo [3/3] Launching RovoDev with MCP enabled...
echo.
echo ========================================
echo   ROVODEV IS READY!
echo ========================================
echo.
echo 🎯 MCP Testing Tools: ENABLED
echo    • Code Review
echo    • Browser Automation  
echo    • Visual AI Analysis (LLaVA)
echo.
echo Starting RovoDev...
echo.

REM Launch RovoDev via PowerShell with full path to acli
powershell -NoExit -Command "cd '%SCRIPT_DIR%'; $env:ROVODEV_MCP_CONFIG='%ROVODEV_MCP_CONFIG%'; & 'C:\Tools\acli\acli.exe' rovodev run"
