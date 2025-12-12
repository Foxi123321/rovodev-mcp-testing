@echo off
cls
echo ========================================
echo   PUBLISH TO GITHUB - AUTOMATED
echo ========================================
echo.

echo This script will:
echo   1. Create the package ZIP
echo   2. Prepare all files
echo   3. Give you the exact git commands to run
echo.

pause

echo.
echo [1/3] Creating package...
call CREATE_PACKAGE_FOR_FRIEND.bat

echo.
echo [2/3] Preparing files for GitHub...
echo.

REM Copy and rename README for GitHub
copy README_GITHUB.md README.md >nul
echo    ✅ README.md ready

REM Files are already in place
echo    ✅ LICENSE ready
echo    ✅ .gitignore ready
echo    ✅ mcp_testing_server/ ready

echo.
echo [3/3] Creating command file...
echo.

REM Create a file with all the git commands
(
echo # COPY AND PASTE THESE COMMANDS IN ORDER
echo.
echo # Step 1: Go to https://github.com/new and create a repository named: rovodev-mcp-testing
echo #         Choose: Public, No README, No .gitignore, No license
echo.
echo # Step 2: Open PowerShell in C:\Users\%USERNAME%\.rovodev and run these commands:
echo.
echo git init
echo git add mcp_testing_server/
echo git add mcp.json
echo git add config.yml
echo git add INSTALL.bat
echo git add README.md
echo git add LICENSE
echo git add .gitignore
echo git add ROVODEV_MCP_TESTING_PACKAGE_README.md
echo git commit -m "Initial commit: RovoDev MCP Testing Server v1.0"
echo.
echo # Step 3: Replace YOUR_USERNAME with your actual GitHub username, then run:
echo.
echo git remote add origin https://github.com/YOUR_USERNAME/rovodev-mcp-testing.git
echo git branch -M main
echo git push -u origin main
echo.
echo # Step 4: Go to your repository on GitHub, click "Releases" > "Create a new release"
echo #         Tag: v1.0.0
echo #         Title: RovoDev MCP Testing Server v1.0
echo #         Upload: RovoDev_MCP_Testing_Package.zip
echo.
echo # DONE! Your project is live!
) > GITHUB_COMMANDS.txt

echo    ✅ GITHUB_COMMANDS.txt created

echo.
echo ========================================
echo   ✅ EVERYTHING READY!
echo ========================================
echo.
echo Next steps:
echo.
echo   1. Open: GITHUB_COMMANDS.txt
echo   2. Follow the instructions
echo   3. Copy-paste the commands
echo.
echo The file has ALL the commands you need!
echo.
pause
