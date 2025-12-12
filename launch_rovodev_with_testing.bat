@echo off
echo ========================================
echo   ROVODEV + MCP TESTING SERVER
echo ========================================
echo.

REM Set the MCP config to include our testing server
set ROVODEV_MCP_CONFIG=%~dp0mcp_testing_config.json

echo Starting Ollama service...
start /B ollama serve >nul 2>&1

echo Waiting for Ollama to start...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   ROVODEV IS READY!
echo ========================================
echo.
echo MCP Testing Server: ENABLED
echo Available AI Models:
ollama list | findstr /C:"qwen3-coder" /C:"llava" /C:"deepseek"
echo.
echo Starting RovoDev...
echo.

REM Launch RovoDev with the MCP config
"%~dp0original_rovodev.exe" run

pause
