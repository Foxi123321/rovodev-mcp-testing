@echo off
cls
echo ========================================
echo   UPDATE README ON GITHUB
echo ========================================
echo.

cd /d "%USERPROFILE%\.rovodev"

echo Copying fixed README...
copy /Y README_GITHUB.md README.md >nul

echo Adding to git...
git add README.md

echo Committing...
git commit -m "docs: Remove EXE references, focus on ZIP package installation"

echo Pushing to GitHub...
git push

if errorlevel 1 (
    echo.
    echo ❌ Push failed!
    echo.
    echo Try: git push origin main
    pause
    exit /b 1
)

echo.
echo ✅ README updated on GitHub!
echo.
echo Opening your repository...
start https://github.com/ggfuc/rovodev-mcp-testing
echo.
echo The README should be updated in a few seconds!
echo.
pause
