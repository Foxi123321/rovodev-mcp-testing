@echo off
REM Start Rovo Dev Server Directly (no wrapper)
cd /d C:\Users\ggfuc\.rovodev

echo Starting Rovo Dev Server directly...
echo.

REM Run directly with acli - SESSION TOKEN ENABLED FOR ANALYTICS
acli rovodev serve 8000 --config-file config_ultimate_bypass.yml --yolo

pause
