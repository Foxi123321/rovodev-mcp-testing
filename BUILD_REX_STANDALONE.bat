@echo off
title REX ROVODEV BUILDER - Watch This Window
echo ========================================
echo REX ROVODEV STANDALONE BUILDER
echo ========================================
echo.
echo Building in separate window so you can see all output...
echo DO NOT CLOSE THIS WINDOW!
echo.

python build_rex_rovodev.py

echo.
echo ========================================
if %errorlevel% equ 0 (
    echo BUILD COMPLETED SUCCESSFULLY!
    echo Check dist\rex_rovodev.exe
) else (
    echo BUILD FAILED - Check errors above
)
echo ========================================
echo.
pause
