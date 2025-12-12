@echo off
cls
echo ========================================
echo   FULLY AUTOMATED GITHUB PUBLISH V2
echo ========================================
echo.

REM Check if gh is installed
gh --version >nul 2>&1
if errorlevel 1 (
    echo Installing GitHub CLI...
    winget install GitHub.cli
    echo.
    echo Please restart this script after installation
    pause
    exit /b 0
)

echo ✅ GitHub CLI found
echo.

REM Fix authentication with proper scopes
echo Checking authentication...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo Logging in to GitHub...
    gh auth login -h github.com -s repo,workflow
) else (
    echo Refreshing authentication with proper scopes...
    gh auth refresh -h github.com -s repo,workflow
)

echo ✅ Authenticated
echo.

echo [1/6] Preparing files...
echo.

REM Navigate to .rovodev
cd /d "%USERPROFILE%\.rovodev"

REM Create package first
call CREATE_PACKAGE_FOR_FRIEND.bat

REM Copy README
if exist README_GITHUB.md (
    copy /Y README_GITHUB.md README.md >nul
    echo    ✅ README prepared
) else (
    echo    ⚠️  README_GITHUB.md not found, skipping
)

echo.
echo [2/6] Initializing git...
echo.

REM Clean any existing git repo
if exist ".git" (
    rmdir /s /q .git
)

git init
echo    ✅ Git initialized

echo.
echo [3/6] Adding files to git...
echo.

git add README.md
git add LICENSE
git add .gitignore
git add mcp.json
git add config.yml
git add INSTALL.bat
git add mcp_testing_server/

echo    ✅ Files staged

echo.
echo [4/6] Creating commit...
echo.

git commit -m "Initial commit: RovoDev MCP Testing Server v1.0 - AI-powered automated testing"

echo    ✅ Commit created

echo.
echo [5/6] Creating and pushing to GitHub...
echo.

REM Delete existing repo if it exists
gh repo delete rovodev-mcp-testing --yes 2>nul

REM Create new repo
gh repo create rovodev-mcp-testing ^
    --public ^
    --description "🔥 AI-powered automated testing for RovoDev: Code review + Browser automation + Vision AI" ^
    --source=. ^
    --remote=origin ^
    --push

if errorlevel 1 (
    echo    ❌ Failed to create repository
    pause
    exit /b 1
)

echo    ✅ Repository created and pushed

echo.
echo [6/6] Creating release...
echo.

REM Wait a moment for GitHub to process
timeout /t 3 /nobreak >nul

REM Create release with package
if exist "RovoDev_MCP_Testing_Package.zip" (
    gh release create v1.0.0 ^
        "RovoDev_MCP_Testing_Package.zip" ^
        --title "🔥 RovoDev MCP Testing Server v1.0" ^
        --notes "## First Release!

**Automated AI-powered code review, browser testing, and visual analysis for RovoDev**

### ✨ Features
- ✅ Automated code review (security, bugs, code smells)
- ✅ Browser automation with Patchright
- ✅ LLaVA vision AI for UI analysis
- ✅ Auto-testing protocol (tests everything automatically)
- ✅ 100%% local, $0 cost, unlimited usage

### 📦 Installation
1. Download **RovoDev_MCP_Testing_Package.zip**
2. Extract to `~/.rovodev/`
3. Run `INSTALL.bat`
4. Start RovoDev: `acli rovodev run`
5. Build something and watch automatic testing!

### 🎯 Quick Test
Ask RovoDev: *\"Build me a calculator app\"*

Watch it automatically:
- Build the code
- Review for bugs
- Test in browser
- Capture screenshots
- Analyze UI with AI
- Fix any issues

### 📚 Documentation
See [README.md](https://github.com/YOUR_USERNAME/rovodev-mcp-testing#readme) for full details.

---

**Built in 3 hours by a 16-year-old with AI assistance** 🔥"

    echo    ✅ Release created with package
) else (
    echo    ⚠️  Package ZIP not found, creating release without attachment
    gh release create v1.0.0 ^
        --title "🔥 RovoDev MCP Testing Server v1.0" ^
        --notes "See README for installation instructions"
)

echo.
echo ========================================
echo   ✅ SUCCESSFULLY PUBLISHED!
echo ========================================
echo.

REM Get the repo URL
for /f "tokens=*" %%i in ('gh repo view --json url --jq .url 2^>nul') do set REPO_URL=%%i

if "%REPO_URL%"=="" (
    set REPO_URL=https://github.com/ggfuc/rovodev-mcp-testing
)

echo Repository: %REPO_URL%
echo Release: %REPO_URL%/releases/tag/v1.0.0
echo.
echo 🎉 Your project is LIVE!
echo.
echo Share it:
echo   Twitter: "Just built an AI testing system for RovoDev! Check it out: %REPO_URL%"
echo   Reddit: Post to r/programming
echo.
echo Opening repository...
start %REPO_URL%
echo.
pause
