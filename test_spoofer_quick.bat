@echo off
echo ================================================================
echo   QUICK SPOOFER TEST
echo ================================================================
echo.
echo This will run a simple command and check if spoofer activates
echo.
pause

echo.
echo Running: rovodev_spoofer.bat run "what is 10+10"
echo.
echo Look for these signs that spoofer is active:
echo   - "REX TOKEN SPOOFER - ACTIVE"
echo   - "REX TOKEN SPOOFER ENABLED"
echo   - "Spoofed llmCount" messages
echo.
echo ================================================================
echo.

call rovodev_spoofer.bat run "what is 10+10"

echo.
echo ================================================================
echo   TEST COMPLETE
echo ================================================================
echo.
echo Checking for real usage file...
if exist .rex_real_usage.json (
    echo [92mSUCCESS! Spoofer created .rex_real_usage.json[0m
    echo.
    echo File contents:
    type .rex_real_usage.json
) else (
    echo [93mNo .rex_real_usage.json found - spoofer may need more usage data[0m
)

echo.
pause
