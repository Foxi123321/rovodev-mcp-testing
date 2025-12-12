@echo off
cls
echo ============================================================
echo.
echo   REX TOKEN SPOOFER - LAUNCH FROM COMPLETE SOURCE
echo.
echo ============================================================
echo.
echo   Step 1: Stopping any running RovoDev servers...
echo.
REM Kill the exe if running
taskkill /F /IM atlassian_cli_rovodev.exe >nul 2>&1
REM Kill only processes on port 3000 (the server), not ALL python processes
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

echo   Step 2: Deploying token spoofer...
echo.

REM Copy token spoofer to .rovodev directory
if not exist "%USERPROFILE%\.rovodev" mkdir "%USERPROFILE%\.rovodev"
copy /Y "token_spoofer.py" "%USERPROFILE%\.rovodev\token_spoofer.py" >nul

REM Set PYTHONPATH to use complete source (has all dependencies)
set PYTHONPATH=%USERPROFILE%\.rovodev;%cd%\rovodev_complete_source;%PYTHONPATH%

echo   ✅ Token spoofer deployed to: %USERPROFILE%\.rovodev\
echo   ✅ PYTHONPATH configured to use complete source
echo.
echo   Step 3: Starting RovoDev from complete source...
echo.
echo   Watch for: "🔥 REX TOKEN SPOOFER ENABLED"
echo.
echo ============================================================
echo.

REM Run RovoDev from complete source - has all dependencies including nemo, nautilus, atlassian_exp
python -c "import sys; sys.path.insert(0, r'%USERPROFILE%\.rovodev'); sys.path.insert(0, r'%cd%\rovodev_complete_source'); from rovodev.__main__ import app; app(['serve', '3000'])"

pause
