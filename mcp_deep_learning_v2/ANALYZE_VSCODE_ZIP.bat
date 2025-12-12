@echo off
title Deep Learning AI - Analyzing VS Code Source
color 0A
cls
echo ================================================================================
echo                   DEEP LEARNING AI - VS CODE ANALYSIS
echo ================================================================================
echo.
echo Target: vscode-main.zip in TEST folder
echo Models: DeepSeek-Coder 33B + Qwen3-Coder 30B
echo.
echo This will:
echo   1. Extract the VS Code source zip
echo   2. Index all functions/classes
echo   3. Run deep AI analysis on everything
echo.
echo Watch this window to see progress in real-time!
echo.
pause

cd /d "%~dp0"

echo.
echo [STEP 1] Extracting VS Code source...
echo ================================================================================

powershell -Command "Expand-Archive -Path 'TEST\vscode-main.zip' -DestinationPath 'TEST\' -Force"

echo Done!
echo.
echo [STEP 2] Starting Deep AI Analysis...
echo ================================================================================
echo.

python analyze_vscode_from_test.py

echo.
echo ================================================================================
echo                              ANALYSIS COMPLETE!
echo ================================================================================
echo.
echo The AIs now know EVERYTHING about VS Code internals!
echo.
pause
