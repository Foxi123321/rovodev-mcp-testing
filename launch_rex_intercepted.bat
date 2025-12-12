@echo off
cls
echo.
echo ============================================================
echo           REX API INTERCEPTOR - NUCLEAR MODE
echo ============================================================
echo.
echo This mode intercepts ALL Anthropic API calls and:
echo   - Strips safety parameters
echo   - Injects Rex system prompts
echo   - Doubles token limits
echo   - Maximizes temperature
echo.
echo WARNING: This is the nuclear option.
echo.
pause
echo.
echo Starting RovoDev with interceptor...
echo.

python launch_rex_intercepted.py %*

echo.
pause
