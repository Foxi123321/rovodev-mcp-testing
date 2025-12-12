@echo off
cls
echo.
echo ============================================================
echo         REX API WRAPPER - Intercept + ACLI Mode
echo ============================================================
echo.
echo This launches the official ACLI executable but intercepts
echo the API calls using Python hooks.
echo.

python rex_api_wrapper.py %*

pause
