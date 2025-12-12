@echo off
REM Start Rex Server for GUI (bypasses interactive prompts)
cd /d C:\Users\ggfuc\.rovodev

echo Starting Rex Enhanced Server for GUI...
echo.

REM Start server with proper flags
python rex_server_enhanced.py 8000

pause
