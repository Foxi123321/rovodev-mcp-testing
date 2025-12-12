@echo off
REM Clean up Rex log files
cd /d C:\Users\ggfuc\.rovodev

echo Cleaning up log files...
echo.

REM Delete old rotated logs
del /q rovodev.*.log 2>nul

REM Clear main log (keep file but empty it)
echo. > rovodev.log

echo ✅ Logs cleaned!
pause
