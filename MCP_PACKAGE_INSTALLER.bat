@echo off
REM ========================================
REM REX MCP SERVERS - MASTER INSTALLER
REM ========================================
echo.
echo ========================================
echo  REX MCP ECOSYSTEM - MASTER INSTALLER
echo ========================================
echo.
echo This will install all dependencies for 6 MCP servers:
echo   1. Knowledge Database (AI-powered code knowledge)
echo   2. Unstoppable Browser (Web automation beast)
echo   3. Sandbox Monitor (Process monitoring)
echo   4. Vision Server (Image analysis with llava)
echo   5. Testing Server (Code review tools)
echo   6. Deep Learning Intelligence (Code analysis)
echo.
pause

REM Check Python
echo.
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Install Python 3.11+ first.
    pause
    exit /b 1
)
echo OK - Python found

REM Install base MCP
echo.
echo [2/7] Installing MCP framework...
pip install mcp>=1.0.0 --quiet
echo OK - MCP installed

REM Install Knowledge Database dependencies
echo.
echo [3/7] Installing Knowledge Database dependencies...
cd mcp_knowledge_db
pip install -r requirements.txt --quiet
cd ..
echo OK - Knowledge DB ready

REM Install Unstoppable Browser dependencies
echo.
echo [4/7] Installing Unstoppable Browser dependencies...
cd mcp_unstoppable_browser
pip install -r requirements.txt --quiet
cd ..
echo OK - Browser ready

REM Install Sandbox Monitor dependencies
echo.
echo [5/7] Installing Sandbox Monitor dependencies...
pip install psutil>=5.9.0 --quiet
echo OK - Sandbox Monitor ready

REM Install Testing Server dependencies
echo.
echo [6/7] Installing Testing Server dependencies...
cd mcp_testing_server
pip install -r requirements.txt --quiet
cd ..
echo OK - Testing Server ready

REM Install Deep Learning dependencies
echo.
echo [7/7] Installing Deep Learning Intelligence dependencies...
cd mcp_deep_learning_v2
pip install -r requirements.txt --quiet
cd ..
echo OK - Deep Learning ready

echo.
echo ========================================
echo  INSTALLATION COMPLETE!
echo ========================================
echo.
echo Next steps:
echo   1. Make sure Ollama is installed and running
echo   2. Run INSTALL_OLLAMA_MODELS.bat to get AI models
echo   3. Copy mcp.json to your RovoDev config directory
echo   4. Launch RovoDev and enjoy!
echo.
pause
