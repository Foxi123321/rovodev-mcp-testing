@echo off
REM THE ULTIMATE REX LAUNCHER
chcp 65001 >nul 2>&1

cls
echo.
echo ============================================================
echo          REX - THE ULTIMATE LAUNCHER
echo ============================================================
echo.
echo This launcher uses:
echo   1. UTF-8 console encoding
echo   2. Monkey-patched Rich library
echo   3. Rex configuration
echo   4. YOLO mode
echo.
pause
echo.

python monkey_patch_rich.py run --yolo %*

echo.
pause
