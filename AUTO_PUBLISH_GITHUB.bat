@echo off
cls
echo ========================================
echo   FULLY AUTOMATED GITHUB PUBLISH
echo ========================================
echo.

REM Check if gh is installed
gh --version >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI not installed!
    echo.
    echo Installing GitHub CLI...
    echo.
    winget install GitHub.cli
    if errorlevel 1 (
        echo.
        echo ❌ Could not install GitHub CLI automatically.
        echo.
        echo Please install manually:
        echo   1. Go to: https://cli.github.com/
        echo   2. Download and install
        echo   3. Run this script again
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ GitHub CLI installed!
    echo Please close this window and run the script again.
    pause
    exit /b 0
)

echo ✅ GitHub CLI found
echo.

REM Check if logged in
gh auth status >nul 2>&1
if errorlevel 1 (
    echo You need to login to GitHub...
    echo.
    echo Opening browser for authentication...
    gh auth login
    if errorlevel 1 (
        echo.
        echo ❌ Authentication failed
        pause
        exit /b 1
    )
)

echo ✅ Authenticated to GitHub
echo.

echo [1/5] Preparing files...
call CREATE_PACKAGE_FOR_FRIEND.bat
copy README_GITHUB.md README.md >nul
echo    ✅ Files ready
echo.

echo [2/5] Initializing git repository...
cd /d "%USERPROFILE%\.rovodev"

git init >nul 2>&1
git add mcp_testing_server/ mcp.json config.yml INSTALL.bat README.md LICENSE .gitignore ROVODEV_MCP_TESTING_PACKAGE_README.md >nul 2>&1
git commit -m "Initial commit: RovoDev MCP Testing Server v1.0" >nul 2>&1
echo    ✅ Git repository initialized
echo.

echo [3/5] Creating GitHub repository...
gh repo create rovodev-mcp-testing --public --description "Automated AI-powered code review, browser testing, and visual analysis for Atlassian RovoDev CLI" --source=. --push
if errorlevel 1 (
    echo.
    echo ⚠️  Repository might already exist or creation failed
    echo    Trying to push to existing repo...
    git remote add origin https://github.com/%USERNAME%/rovodev-mcp-testing.git 2>nul
    git branch -M main >nul 2>&1
    git push -u origin main
)
echo    ✅ Repository created and pushed
echo.

echo [4/5] Creating GitHub release...

REM Create release description
(
echo 🔥 First Release!
echo.
echo Automated AI-powered code review, browser testing, and visual analysis for RovoDev.
echo.
echo ### Features
echo - ✅ Automated code review
echo - ✅ Browser automation with Patchright
echo - ✅ LLaVA vision AI analysis  
echo - ✅ Auto-testing protocol
echo - ✅ 100%% local, $0 cost
echo.
echo ### Installation
echo Download `RovoDev_MCP_Testing_Package.zip` and run `INSTALL.bat`
echo.
echo ### Quick Start
echo 1. Extract ZIP to `~/.rovodev/`
echo 2. Run `INSTALL.bat`
echo 3. Start RovoDev: `acli rovodev run`
echo 4. Ask it to build something and watch auto-testing!
echo.
echo See README for full documentation.
) > release_notes.txt

REM Create release with the package
gh release create v1.0.0 ^
    RovoDev_MCP_Testing_Package.zip ^
    --title "RovoDev MCP Testing Server v1.0" ^
    --notes-file release_notes.txt

del release_notes.txt
echo    ✅ Release v1.0.0 created
echo.

echo [5/5] Getting repository URL...
for /f "tokens=*" %%i in ('gh repo view --json url -q .url') do set REPO_URL=%%i
echo.

echo ========================================
echo   ✅ PUBLISHED TO GITHUB!
echo ========================================
echo.
echo Your repository: %REPO_URL%
echo Release: %REPO_URL%/releases/tag/v1.0.0
echo.
echo 🎉 Your project is now live!
echo.
echo Next steps:
echo   • Share on Twitter/X
echo   • Post on Reddit r/programming
echo   • Add topics to the repo (click Settings > Topics)
echo   • Star your own repo 😂
echo.
echo Opening your repository...
start %REPO_URL%
echo.
pause
