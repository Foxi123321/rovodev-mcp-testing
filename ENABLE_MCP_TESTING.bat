@echo off
echo ========================================
echo   ENABLE MCP TESTING SERVER
echo ========================================
echo.

REM Set the environment variable permanently for current user
set MCP_CONFIG=%~dp0mcp_testing_config.json

echo Setting ROVODEV_MCP_CONFIG environment variable...
setx ROVODEV_MCP_CONFIG "%MCP_CONFIG%"

echo.
echo ========================================
echo   ✅ MCP TESTING SERVER ENABLED!
echo ========================================
echo.
echo Config set to: %MCP_CONFIG%
echo.
echo Next time you run:
echo   acli rovodev run
echo.
echo The MCP Testing Server will be available!
echo.
echo 🎯 Available Tools:
echo    • review_code
echo    • browser_navigate
echo    • browser_click
echo    • browser_screenshot
echo    • analyze_screenshot
echo    • detect_ui_issues
echo.
echo ⚠️  NOTE: Close this window and open a NEW PowerShell
echo    for the environment variable to take effect!
echo.
pause
