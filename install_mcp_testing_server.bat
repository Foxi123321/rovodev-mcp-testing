@echo off
echo ========================================
echo   INSTALLING MCP TESTING SERVER
echo ========================================
echo.

cd mcp_testing_server

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Installing Patchright browsers...
patchright install chromium

echo.
echo [3/3] Creating screenshots directory...
if not exist "screenshots" mkdir screenshots

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start the server, run:
echo   start_mcp_testing_server.bat
echo.
pause
