@echo off
cls
echo ============================================================
echo.
echo   REX TOKEN SPOOFER - LAUNCH SEQUENCE
echo.
echo ============================================================
echo.
echo   Step 1: Stopping any running RovoDev servers...
echo.
taskkill /F /IM atlassian_cli_rovodev.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo   Step 2: Deploying token spoofer...
echo.

REM Copy token spoofer to .rovodev directory
if not exist "%USERPROFILE%\.rovodev" mkdir "%USERPROFILE%\.rovodev"
copy /Y "%cd%\token_spoofer.py" "%USERPROFILE%\.rovodev\token_spoofer.py" >nul

REM Also copy to current directory as fallback
copy /Y "%cd%\token_spoofer.py" "token_spoofer.py" >nul

REM Set PYTHONPATH to include both locations
set PYTHONPATH=%USERPROFILE%\.rovodev;%cd%;%PYTHONPATH%

echo   ✅ Token spoofer deployed to: %USERPROFILE%\.rovodev\
echo   ✅ PYTHONPATH configured
echo.
echo   Step 3: Starting RovoDev with spoofer enabled...
echo.
echo   Watch for: "🔥 REX TOKEN SPOOFER ENABLED"
echo.
echo ============================================================
echo.

REM Start server - spoofer will auto-load from __main__.py
acli rovodev serve 3000

pause
