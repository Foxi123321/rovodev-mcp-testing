@echo off
title Deep Learning AI - Code Analysis
color 0A
echo ========================================
echo  DEEP LEARNING AI - CODE ANALYZER
echo ========================================
echo.
echo This will analyze ANY codebase you point it at
echo Both DeepSeek 33B and Qwen 30B will learn it!
echo.
set /p CODE_PATH="Enter path to code: "
echo.
echo Starting analysis of: %CODE_PATH%
echo.
pause

cd /d "%~dp0"
python analyze_any_code.py "%CODE_PATH%"

echo.
echo ========================================
echo  ANALYSIS COMPLETE!
echo ========================================
pause
