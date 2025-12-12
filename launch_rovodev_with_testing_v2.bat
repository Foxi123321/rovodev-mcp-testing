@echo off
cls
echo ========================================
echo   ROVODEV + MCP TESTING SERVER
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Set the MCP config to include our testing server
set MCP_CONFIG=%SCRIPT_DIR%mcp_testing_config.json

echo [1/3] Starting Ollama service...
start /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✅ Ollama started
echo.

echo [2/3] Checking AI models...
ollama list | findstr /C:"qwen3-coder" /C:"llava"
echo.

echo [3/3] Starting RovoDev with MCP Testing Server...
echo.
echo ========================================
echo   ROVODEV IS READY!
echo ========================================
echo.
echo MCP Testing Server: ENABLED
echo Config: %MCP_CONFIG%
echo.

REM Set environment variable for RovoDev to use our MCP config
set ROVODEV_MCP_CONFIG=%MCP_CONFIG%

REM Launch the original rovodev.exe
"%SCRIPT_DIR%original_rovodev.exe" run

pause
