@echo off
REM ========================================
REM START ALL MCP SERVERS (FOR TESTING)
REM ========================================
echo.
echo ========================================
echo  STARTING ALL MCP SERVERS
echo ========================================
echo.
echo NOTE: Normally these are auto-started by RovoDev.
echo This is for manual testing only.
echo.

REM Set environment
set OLLAMA_BASE_URL=http://localhost:11434

echo Starting servers in separate windows...
echo.

echo [1/6] Knowledge Database...
start "MCP - Knowledge DB" python "%~dp0mcp_knowledge_db\server.py"
timeout /t 2 /nobreak >nul

echo [2/6] Unstoppable Browser...
start "MCP - Browser" python "%~dp0mcp_unstoppable_browser\server.py"
timeout /t 2 /nobreak >nul

echo [3/6] Sandbox Monitor...
start "MCP - Sandbox" python "%~dp0mcp_sandbox_monitor\server.py"
timeout /t 2 /nobreak >nul

echo [4/6] Vision Server...
start "MCP - Vision" python "%~dp0mcp_vision_simple\server.py"
timeout /t 2 /nobreak >nul

echo [5/6] Testing Server...
start "MCP - Testing" python "%~dp0mcp_testing_server\server.py"
timeout /t 2 /nobreak >nul

echo [6/6] Deep Learning Intelligence...
set PYTHONPATH=%~dp0mcp_deep_learning_v2
start "MCP - Deep Learning" python "%~dp0mcp_deep_learning_v2\server.py"

echo.
echo ========================================
echo  ALL SERVERS STARTED!
echo ========================================
echo.
echo Check the separate windows for each server.
echo Close windows to stop servers.
echo.
pause
