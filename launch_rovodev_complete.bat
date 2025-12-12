@echo off
cls
echo ========================================
echo   ROVODEV + MCP TESTING SERVER
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set ROVODEV_DIR=%SCRIPT_DIR%rovodev_complete_source

REM Set the MCP config to include our testing server
set MCP_CONFIG=%SCRIPT_DIR%mcp_testing_config.json
set ROVODEV_MCP_CONFIG=%MCP_CONFIG%

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
echo Working Dir: %ROVODEV_DIR%
echo.

REM Change to rovodev_complete_source directory where all DLLs are
cd /d "%ROVODEV_DIR%"

REM Check if atlassian_cli_rovodev_rex.exe exists
if exist "atlassian_cli_rovodev_rex.exe" (
    echo Launching RovoDev...
    echo.
    atlassian_cli_rovodev_rex.exe run
) else (
    echo ERROR: RovoDev executable not found!
    echo.
    dir /b *.exe
    pause
)
