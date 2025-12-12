@echo off
echo ========================================
echo REX ROVODEV STANDALONE LAUNCHER
echo ========================================
echo.

REM Check if built
if not exist "dist\rex_rovodev.exe" (
    echo ERROR: rex_rovodev.exe not found in dist\
    echo.
    echo Run build_rex_rovodev.py first:
    echo   python build_rex_rovodev.py
    echo.
    pause
    exit /b 1
)

REM Copy token_spoofer to current directory if not present
if not exist "token_spoofer.py" (
    echo Copying token_spoofer.py to current directory...
    copy dist\token_spoofer.py . >nul 2>&1
)

echo Starting REX ROVODEV with token spoofer enabled...
echo.

REM Run the standalone executable
dist\rex_rovodev.exe %*

echo.
echo REX ROVODEV session ended.
pause
