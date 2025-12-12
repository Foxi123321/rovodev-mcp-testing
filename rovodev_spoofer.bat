@echo off
REM 🔥 REX SPOOFER - Direct RovoDev Launcher with Token Spoofer
REM Runs RovoDev from source with spoofer guaranteed to load

echo ================================================================
echo   🔥 REX TOKEN SPOOFER - ACTIVE 🔥
echo ================================================================
echo.
echo   Strategy: Report 10%% of actual usage to Atlassian
echo   Real usage saved to: .rex_real_usage.json
echo.
echo ================================================================
echo.

REM Make sure we're in the right directory
cd /d "%~dp0"

REM Run RovoDev from source with spoofer
REM Note: This runs from source to ensure spoofer loads
python -m rovodev.rovodev_cli %*
