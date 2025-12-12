@echo off
cls
echo ========================================
echo   ROVODEV + MCP TESTING - QUICK START
echo ========================================
echo.

REM Set MCP config for this session only
set ROVODEV_MCP_CONFIG=%~dp0mcp_testing_config.json

echo [1/3] Starting Ollama...
start /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✅ Ollama started
echo.

echo [2/3] Starting MCP Testing Server...
start "MCP Testing Server" /MIN cmd /c "cd mcp_testing_server && python server.py"
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
echo.
echo 🤖 AI Models Available:
ollama list | findstr /C:"qwen3-coder" /C:"llava" /C:"deepseek"
echo.
echo Starting RovoDev...
echo.

REM Launch RovoDev
acli rovodev run

pause
