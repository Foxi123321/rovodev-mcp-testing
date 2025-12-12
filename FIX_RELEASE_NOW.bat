@echo off
cls
echo ========================================
echo   FIX GITHUB RELEASE (Add Package ZIP)
echo ========================================
echo.

cd /d "%USERPROFILE%\.rovodev"

echo Checking for package ZIP...
if not exist "RovoDev_MCP_Testing_Package.zip" (
    echo Package ZIP not found! Creating it now...
    call CREATE_PACKAGE_FOR_FRIEND.bat
)

if not exist "RovoDev_MCP_Testing_Package.zip" (
    echo ❌ Could not create package ZIP!
    pause
    exit /b 1
)

echo ✅ Package ZIP found
echo.

echo Uploading to GitHub release v1.0.0...
gh release upload v1.0.0 "RovoDev_MCP_Testing_Package.zip" --clobber

if errorlevel 1 (
    echo.
    echo ❌ Upload failed!
    echo.
    echo Make sure:
    echo   1. You ran AUTO_PUBLISH_GITHUB_V2.bat first
    echo   2. The release v1.0.0 exists
    echo   3. You're authenticated to GitHub
    pause
    exit /b 1
)

echo.
echo ✅ Package ZIP uploaded successfully!
echo.
echo Opening your release...
start https://github.com/ggfuc/rovodev-mcp-testing/releases/tag/v1.0.0
echo.
echo Your release now has the downloadable ZIP!
echo.
pause
