@echo off
REM Ultimate Rex launcher with all fixes
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

cls
echo.
echo ============================================================
echo        REX ULTIMATE - ALL FIXES APPLIED
echo ============================================================
echo.
echo Configuration:
echo   - UTF-8 encoding forced
echo   - Rex personality active
echo   - YOLO mode enabled
echo   - API interceptor ready
echo.
pause
echo.

REM Option 1: Try with Python wrapper
echo Attempting launch with UTF-8 wrapper...
python console_wrapper.py run --yolo %*

REM If that fails, try direct
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Wrapper failed, trying direct...
    acli rovodev run --yolo %*
)

pause
