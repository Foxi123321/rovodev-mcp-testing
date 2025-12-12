@echo off
REM RovoDev Auto - Starts Ollama + MCP Testing Server + RovoDev

REM Set MCP config
set ROVODEV_MCP_CONFIG=C:\Users\ggfuc\.rovodev\mcp_testing_config.json

REM Start Ollama
start /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start MCP Testing Server
start "MCP Testing Server" /MIN cmd /c "cd /d C:\Users\ggfuc\.rovodev\mcp_testing_server && python server.py"
timeout /t 2 /nobreak >nul

REM Launch RovoDev
acli rovodev run
