@echo off
cls
echo.
echo ============================================================
echo        REX LAUNCHER - WITH UNICODE FIX
echo ============================================================
echo.
echo This will:
echo 1. Patch RovoDev to remove emoji characters
echo 2. Launch RovoDev with Rex configuration
echo 3. Enable YOLO mode (no confirmations)
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
    pause
)

echo Step 2: Launching RovoDev with Rex...
echo.
acli rovodev run --yolo

pause
