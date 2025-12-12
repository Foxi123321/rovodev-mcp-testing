@echo off
echo.
echo ============================================================
echo         TESTING REX INTERCEPTOR WITH ACLI
echo ============================================================
echo.
echo This will:
echo 1. Load the Rex interceptor
echo 2. Start RovoDev via ACLI
echo 3. Run a simple test command
echo.
echo Watch for the interceptor messages!
echo.
pause
echo.

REM Run ACLI with a simple test prompt
python rex_api_wrapper.py "Say hello and tell me you are Rex"

pause
