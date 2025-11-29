@echo off
cls
echo ========================================
echo   ROVODEV MCP TESTING SERVER
echo   Installation Script
echo ========================================
echo.

REM Get current directory
set INSTALL_DIR=%~dp0

echo This will install:
echo   - MCP Testing Server
echo   - Python dependencies
echo   - Patchright browser
echo   - LLaVA vision model
echo.

echo Installation directory: %INSTALL_DIR%
echo.

pause

echo.
echo [1/5] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo    Please install Python from https://python.org
    echo    Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
echo    ✅ Python found

REM Check Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    where /q ollama.exe
    if errorlevel 1 (
        echo ⚠️  Ollama not found in PATH
        echo    Checking common locations...
        if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
            echo    ✅ Ollama found
        ) else (
            echo    ❌ Ollama not installed!
            echo    Please install from https://ollama.com
            pause
            exit /b 1
        )
    ) else (
        echo    ✅ Ollama found
    )
) else (
    echo    ✅ Ollama found
)

REM Check acli
acli --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  RovoDev (acli) not found or not in PATH
    echo    Make sure RovoDev is installed properly
) else (
    echo    ✅ RovoDev found
)

echo.
echo [2/5] Installing Python dependencies...
echo.

cd /d "%INSTALL_DIR%mcp_testing_server"
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo    ✅ Dependencies installed

echo.
echo [3/5] Installing Patchright browser...
echo.

patchright install chromium
if errorlevel 1 (
    echo ⚠️  Patchright install had warnings (this is usually okay)
)
echo    ✅ Patchright ready

echo.
echo [4/5] Downloading LLaVA vision model (this may take 5-10 minutes)...
echo.

REM Try to find ollama
set OLLAMA_PATH=ollama
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set OLLAMA_PATH=%LOCALAPPDATA%\Programs\Ollama\ollama.exe
)

"%OLLAMA_PATH%" pull llava:7b
if errorlevel 1 (
    echo ⚠️  Failed to download LLaVA (you can do this manually later)
    echo    Run: ollama pull llava:7b
) else (
    echo    ✅ LLaVA model downloaded
)

echo.
echo [5/5] Verifying installation...
echo.

cd /d "%INSTALL_DIR%"

if exist "mcp.json" (
    echo    ✅ MCP config found
) else (
    echo    ⚠️  mcp.json not found - you may need to configure manually
)

if exist "mcp_testing_server\server.py" (
    echo    ✅ MCP server found
) else (
    echo    ❌ MCP server not found!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start RovoDev with MCP Testing enabled:
echo.
echo    acli rovodev run
echo.
echo Then ask it to build something and watch the magic!
echo.
echo Example: "Build me a todo list app"
echo.
echo See ROVODEV_MCP_TESTING_PACKAGE_README.md for more info.
echo.
pause
