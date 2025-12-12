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
set ROVODEV_MCP_CONFIG=%MCP_CONFIG%

echo [1/3] Starting Ollama service...
start /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✅ Ollama started
echo.

echo [2/3] MCP Testing Server Status...
echo       ✅ ENABLED
echo       Config: %MCP_CONFIG%
echo.

echo [3/3] Available AI Models...
ollama list | findstr /C:"qwen3-coder" /C:"llava" /C:"deepseek"
echo.

echo ========================================
echo   STARTING ROVODEV
echo ========================================
echo.
echo 🎯 MCP Testing Tools Available:
echo    • review_code - Analyze code for bugs
echo    • browser_navigate - Open websites
echo    • browser_click - Click elements
echo    • browser_screenshot - Capture pages
echo    • analyze_screenshot - AI visual analysis
echo    • detect_ui_issues - Find UI bugs
echo.
echo 🚀 Ready to build and test automatically!
echo.

REM Launch RovoDev
"%SCRIPT_DIR%target_executable.exe" run

pause
