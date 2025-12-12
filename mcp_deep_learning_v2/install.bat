@echo off
echo ===============================================
echo Deep Learning Intelligence v2 - Installation
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Checking Ollama installation...
ollama list >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama not found or not running
    echo Please ensure Ollama is installed and running
    echo Download from: https://ollama.ai
    echo.
) else (
    echo Ollama is running!
)

echo.
echo [3/4] Checking for required models...
ollama list | findstr "deepseek-coder:33b" >nul
if errorlevel 1 (
    echo WARNING: deepseek-coder:33b not found
    echo Run: ollama pull deepseek-coder:33b
    echo.
) else (
    echo ✓ deepseek-coder:33b found
)

ollama list | findstr "qwen3-coder:30b" >nul
if errorlevel 1 (
    echo WARNING: qwen3-coder:30b not found  
    echo Run: ollama pull qwen3-coder:30b
    echo.
) else (
    echo ✓ qwen3-coder:30b found
)

echo.
echo [4/4] Creating data directory...
python -c "from config import DATA_DIR; DATA_DIR.mkdir(parents=True, exist_ok=True); print(f'Created: {DATA_DIR}')"

echo.
echo ===============================================
echo Installation Complete!
echo ===============================================
echo.
echo The MCP server is ready to use.
echo.
echo To test it, run: python server.py
echo.
echo Add this to your mcp.json:
echo {
echo   "deep-learning-v2": {
echo     "command": "python",
echo     "args": ["C:/path/to/mcp_deep_learning_v2/server.py"],
echo     "env": {
echo       "OLLAMA_BASE_URL": "http://localhost:11434"
echo     }
echo   }
echo }
echo.
pause
