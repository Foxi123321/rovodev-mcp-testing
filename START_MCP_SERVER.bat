@echo off
echo ========================================
echo   STARTING MCP TESTING SERVER
echo ========================================
echo.

cd mcp_testing_server
echo Server Location: %CD%
echo.

echo Starting server...
echo (Keep this window open!)
echo.

python server.py

pause
