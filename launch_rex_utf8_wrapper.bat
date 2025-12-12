@echo off
REM Force UTF-8 before launching RovoDev
chcp 65001 >nul 2>&1

cls
echo.
echo ============================================================
echo        REX LAUNCHER - UTF-8 WRAPPER
echo ============================================================
echo.
echo This forces UTF-8 encoding before launching RovoDev
echo to avoid Unicode crashes.
echo.

python console_wrapper.py run --yolo %*

pause
