@echo off
cls
echo.
echo ============================================================
echo    REX LAUNCHER - WITH UNICODE FIX + API INTERCEPTOR
echo ============================================================
echo.
echo This will:
echo 1. Patch RovoDev to remove emoji characters
echo 2. Load API interceptor
echo 3. Launch RovoDev with Rex configuration
echo.
pause
echo.

echo Step 1: Applying Unicode fix...
python fix_rovodev_unicode.py
echo.

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Warning: Unicode fix failed, but continuing anyway...
    echo.
)

echo Step 2: Launching with API interceptor...
echo.
python rex_api_wrapper.py

pause
