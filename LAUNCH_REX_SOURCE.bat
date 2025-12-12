@echo off
cls
echo ============================================================
echo.
echo   Step 1: Stopping any running RovoDev servers...
echo.
taskkill /F /IM atlassian_cli_rovodev.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo   Step 2: Starting RovoDev from SOURCE (with spoofer)...
echo.
echo   Watch for: "🔥 REX TOKEN SPOOFER ENABLED"
echo.
echo ============================================================
echo.

REM Run from Python source
python launch_rex_from_source.py serve

pause
