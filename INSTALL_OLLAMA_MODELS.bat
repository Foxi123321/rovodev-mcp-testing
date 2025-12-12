@echo off
REM ========================================
REM OLLAMA AI MODELS INSTALLER
REM ========================================
echo.
echo ========================================
echo  OLLAMA AI MODELS INSTALLER
echo ========================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama not found!
    echo.
    echo Please install Ollama first:
    echo https://ollama.com/download
    echo.
    pause
    exit /b 1
)

echo Ollama found! Checking if service is running...
ollama list >nul 2>&1
if errorlevel 1 (
    echo.
    echo Starting Ollama service...
    start "" ollama serve
    timeout /t 5 /nobreak >nul
)

echo.
echo This will download the following AI models:
echo.
echo   1. gemma2:9b        (5.4 GB) - Fast, accurate code analysis
echo   2. llava:latest     (4.7 GB) - Vision AI for image analysis
echo   3. qwen2.5:14b      (9.0 GB) - Alternative code model
echo.
echo Total download: ~19 GB
echo This may take 30-60 minutes depending on your connection.
echo.
set /p continue="Continue? (y/n): "
if /i not "%continue%"=="y" exit /b 0

echo.
echo ========================================
echo Installing AI Models...
echo ========================================

echo.
echo [1/3] Downloading gemma2:9b (for code analysis)...
ollama pull gemma2:9b

echo.
echo [2/3] Downloading llava:latest (for vision)...
ollama pull llava:latest

echo.
echo [3/3] Downloading qwen2.5:14b (backup code model)...
ollama pull qwen2.5:14b

echo.
echo ========================================
echo  ALL MODELS INSTALLED!
echo ========================================
echo.
echo Installed models:
ollama list
echo.
echo You're ready to use the MCP servers!
echo.
pause
