@echo off
REM Set UTF-8 encoding to avoid unicode errors
chcp 65001 >nul

cls
echo.
echo ============================================================
echo              REX SYSTEM - FINAL LIVE TEST
echo ============================================================
echo.
echo This will test the complete Rex setup:
echo   1. Config with Rex personality
echo   2. YOLO mode (no confirmations)
echo   3. Temperature 1.0
echo   4. All permissions allowed
echo.
echo The test will ask Rex to introduce himself.
echo Watch for the Rex personality in the response!
echo.
pause
echo.

REM Run the test
acli rovodev run --yolo "Who are you? Introduce yourself as Rex in 2 sentences."

echo.
echo ============================================================
echo Test complete!
echo.
pause
