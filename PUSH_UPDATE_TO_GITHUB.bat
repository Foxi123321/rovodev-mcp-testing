@echo off
cls
echo ========================================
echo   PUSH UPDATE TO GITHUB
echo ========================================
echo.

cd /d "%USERPROFILE%\.rovodev"

echo [1/3] Adding changed files...
echo.

git add mcp_testing_server/
git add README.md
git add README_GITHUB.md

echo    ✅ Files staged
echo.

echo [2/3] Committing changes...
echo.

git commit -m "feat: Add browser_restart tool to recover from crashes

- Added browser_restart() function to handle crashed browser contexts
- Improved error handling and state management
- Fixed README to remove EXE references
- Now focuses on ZIP package installation"

if errorlevel 1 (
    echo.
    echo ⚠️  Nothing to commit or commit failed
    echo    (This might mean no changes were detected)
    echo.
)

echo.
echo [3/3] Pushing to GitHub...
echo.

git push

if errorlevel 1 (
    echo.
    echo ❌ Push failed!
    echo.
    echo Try manually: git push origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ UPDATE PUSHED TO GITHUB!
echo ========================================
echo.
echo Changes:
echo   • browser_restart tool added
echo   • README fixed (no EXE mentions)
echo   • Better error handling
echo.
echo Opening your repository...
start https://github.com/ggfuc/rovodev-mcp-testing
echo.
echo Your project is now even better! 🔥
echo.
pause
