@echo off
title Deep Learning AI - Analyzing VS Code
color 0A
echo ========================================
echo  DEEP LEARNING AI - VS CODE ANALYSIS
echo ========================================
echo.
echo This will index and analyze VS Code source code
echo Both DeepSeek 33B and Qwen 30B will learn everything!
echo.
echo This will take a WHILE (VS Code is huge)
echo Watch this window to see progress...
echo.
pause

cd /d "%~dp0"
python analyze_vscode.py

echo.
echo ========================================
echo  ANALYSIS COMPLETE!
echo ========================================
pause
