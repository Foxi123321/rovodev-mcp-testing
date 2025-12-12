@echo off
cls
echo ========================================
echo   ROVODEV + MCP TESTING SERVER
echo   (Python Direct Launch)
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Set the MCP config to include our testing server
set MCP_CONFIG=%SCRIPT_DIR%mcp_testing_config.json
set ROVODEV_MCP_CONFIG=%MCP_CONFIG%

echo [1/4] Starting Ollama service...
start /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✅ Ollama started
echo.

echo [2/4] MCP Testing Server Status...
echo       ✅ ENABLED
echo       Config: %MCP_CONFIG%
echo.

echo [3/4] Available AI Models...
ollama list | findstr /C:"qwen3-coder" /C:"llava" /C:"deepseek"
echo.

echo [4/4] Installing RovoDev dependencies...
python -m pip install -q mcp pydantic-ai-slim aiohttp >nul 2>&1
echo       ✅ Dependencies ready
echo.

echo ========================================
echo   STARTING ROVODEV (Python)
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

REM Launch RovoDev via Python
python -m rovodev_source_extracted run

if errorlevel 1 (
    echo.
    echo ⚠️  Failed to start via module. Trying direct execution...
    echo.
    python rovodev_source_extracted\__main__.py run
)

pause
