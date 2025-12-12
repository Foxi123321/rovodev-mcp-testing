@echo off
REM ========================================
REM ROVODEV MCP TESTING PACKAGE INSTALLER
REM ========================================
echo.
echo ========================================
echo  ROVODEV MCP TESTING PACKAGE
echo  Automated Installer v1.0
echo ========================================
echo.
echo This will install 6 powerful MCP servers:
echo   1. Knowledge Database (AI code intelligence)
echo   2. Unstoppable Browser (Web automation)
echo   3. Sandbox Monitor (Process monitoring)
echo   4. Vision Server (Image analysis)
echo   5. Testing Server (Code review)
echo   6. Deep Learning Intelligence (Semantic search)
echo.
echo Installation will take 5-10 minutes.
echo.
pause

REM ========================================
REM STEP 1: Environment Check
REM ========================================
echo.
echo [Step 1/8] Checking environment...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Python 3.11+ is required. Please install from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo   [OK] Python found

REM Check if we're in the right directory
if not exist "mcp_knowledge_db" (
    if not exist ".rovodev" (
        echo [ERROR] Wrong directory!
        echo.
        echo Please run this from your .rovodev directory:
        echo   C:\Users\YourName\.rovodev\
        echo.
        pause
        exit /b 1
    )
)
echo   [OK] Directory structure looks good

REM ========================================
REM STEP 2: Install Base MCP Framework
REM ========================================
echo.
echo [Step 2/8] Installing MCP framework...
echo.
pip install mcp>=1.0.0 --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install MCP framework
    pause
    exit /b 1
)
echo   [OK] MCP framework installed

REM ========================================
REM STEP 3: Install Knowledge Database
REM ========================================
echo.
echo [Step 3/8] Installing Knowledge Database...
echo.
cd mcp_knowledge_db 2>nul || (
    echo [ERROR] mcp_knowledge_db directory not found!
    pause
    exit /b 1
)
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install Knowledge Database dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo   [OK] Knowledge Database ready

REM ========================================
REM STEP 4: Install Unstoppable Browser
REM ========================================
echo.
echo [Step 4/8] Installing Unstoppable Browser...
echo.
cd mcp_unstoppable_browser 2>nul || (
    echo [ERROR] mcp_unstoppable_browser directory not found!
    pause
    exit /b 1
)
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install Browser dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo   [OK] Unstoppable Browser ready

REM ========================================
REM STEP 5: Install Sandbox Monitor
REM ========================================
echo.
echo [Step 5/8] Installing Sandbox Monitor...
echo.
pip install psutil>=5.9.0 --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install Sandbox Monitor dependencies
    pause
    exit /b 1
)
echo   [OK] Sandbox Monitor ready

REM ========================================
REM STEP 6: Install Vision Server
REM ========================================
echo.
echo [Step 6/8] Installing Vision Server...
echo.
cd mcp_vision_simple 2>nul || (
    echo [WARNING] mcp_vision_simple directory not found, skipping...
    cd .. 2>nul
    goto skip_vision
)
REM Vision server has minimal deps, just make sure directory exists
cd ..
:skip_vision
echo   [OK] Vision Server ready

REM ========================================
REM STEP 7: Install Testing Server
REM ========================================
echo.
echo [Step 7/8] Installing Testing Server...
echo.
cd mcp_testing_server 2>nul || (
    echo [ERROR] mcp_testing_server directory not found!
    pause
    exit /b 1
)
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install Testing Server dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo   [OK] Testing Server ready

REM ========================================
REM STEP 8: Install Deep Learning Intelligence
REM ========================================
echo.
echo [Step 8/8] Installing Deep Learning Intelligence...
echo.
cd mcp_deep_learning_v2 2>nul || (
    echo [ERROR] mcp_deep_learning_v2 directory not found!
    pause
    exit /b 1
)
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install Deep Learning dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo   [OK] Deep Learning Intelligence ready

REM ========================================
REM CONFIGURATION CHECK
REM ========================================
echo.
echo [Configuration] Checking MCP configuration...
echo.

if exist "mcp.json" (
    echo   [OK] mcp.json found
) else (
    if exist "mcp-servers.json" (
        echo   [OK] mcp-servers.json found
    ) else (
        echo   [WARNING] No MCP configuration file found
        echo   You may need to manually configure RovoDev
    )
)

REM ========================================
REM SUCCESS!
REM ========================================
echo.
echo ========================================
echo  INSTALLATION COMPLETE!
echo ========================================
echo.
echo All 6 MCP servers are now installed!
echo.
echo NEXT STEPS:
echo.
echo   1. Install Ollama (if not already installed):
echo      https://ollama.com/download
echo.
echo   2. Download AI models:
echo      Run: INSTALL_OLLAMA_MODELS.bat
echo      (This takes 30-60 minutes, ~19 GB download)
echo.
echo   3. Test the installation:
echo      Run: TEST_MCP_SERVERS.bat
echo.
echo   4. Restart RovoDev
echo      The MCP servers will auto-connect!
echo.
echo ========================================
echo.
pause
