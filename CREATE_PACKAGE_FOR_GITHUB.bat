@echo off
REM ========================================
REM CREATE GITHUB RELEASE PACKAGE
REM ========================================
echo.
echo ========================================
echo  CREATE GITHUB RELEASE PACKAGE
echo ========================================
echo.
echo This will create a distributable package for GitHub.
echo.
pause

REM Create package directory
set PACKAGE_DIR=rovodev_mcp_testing_package
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo.
echo [1/5] Creating package directory...
if exist "%PACKAGE_DIR%" (
    echo   Removing old package...
    rmdir /s /q "%PACKAGE_DIR%"
)
mkdir "%PACKAGE_DIR%"
echo   [OK] Directory created

REM ========================================
REM Copy MCP Server Directories
REM ========================================
echo.
echo [2/5] Copying MCP servers...

echo   - Knowledge Database...
xcopy /E /I /Q mcp_knowledge_db "%PACKAGE_DIR%\mcp_knowledge_db\" >nul
if errorlevel 1 echo     [WARNING] Copy failed

echo   - Unstoppable Browser...
xcopy /E /I /Q mcp_unstoppable_browser "%PACKAGE_DIR%\mcp_unstoppable_browser\" >nul
if errorlevel 1 echo     [WARNING] Copy failed

echo   - Sandbox Monitor...
xcopy /E /I /Q mcp_sandbox_monitor "%PACKAGE_DIR%\mcp_sandbox_monitor\" >nul
if errorlevel 1 echo     [WARNING] Copy failed

echo   - Vision Server...
xcopy /E /I /Q mcp_vision_simple "%PACKAGE_DIR%\mcp_vision_simple\" >nul
if errorlevel 1 echo     [WARNING] Copy failed

echo   - Testing Server...
xcopy /E /I /Q mcp_testing_server "%PACKAGE_DIR%\mcp_testing_server\" >nul
if errorlevel 1 echo     [WARNING] Copy failed

echo   - Deep Learning Intelligence...
xcopy /E /I /Q mcp_deep_learning_v2 "%PACKAGE_DIR%\mcp_deep_learning_v2\" >nul
if errorlevel 1 echo     [WARNING] Copy failed

echo   [OK] All servers copied

REM ========================================
REM Copy Configuration Files
REM ========================================
echo.
echo [3/5] Copying configuration files...

if exist "mcp.json" (
    copy /Y mcp.json "%PACKAGE_DIR%\mcp.json" >nul
    echo   [OK] mcp.json copied
) else (
    echo   [WARNING] mcp.json not found
)

if exist "mcp-servers.json" (
    copy /Y mcp-servers.json "%PACKAGE_DIR%\mcp-servers.json" >nul
    echo   [OK] mcp-servers.json copied
)

REM ========================================
REM Copy Install Scripts
REM ========================================
echo.
echo [4/5] Copying install scripts...

copy /Y INSTALL_MCP_TESTING.bat "%PACKAGE_DIR%\" >nul
copy /Y INSTALL_OLLAMA_MODELS.bat "%PACKAGE_DIR%\" >nul
copy /Y TEST_MCP_SERVERS.bat "%PACKAGE_DIR%\" >nul
copy /Y START_ALL_MCP_SERVERS.bat "%PACKAGE_DIR%\" >nul
copy /Y ROVODEV_MCP_TESTING_PACKAGE_README.md "%PACKAGE_DIR%\README.md" >nul

echo   [OK] All scripts copied

REM ========================================
REM Create Archive
REM ========================================
echo.
echo [5/5] Creating ZIP archive...

REM Check if PowerShell is available for compression
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%PACKAGE_DIR%_%TIMESTAMP%.zip' -Force" 2>nul
if errorlevel 1 (
    echo   [WARNING] PowerShell compression failed
    echo   Package directory created but not zipped.
    echo   Please manually zip: %PACKAGE_DIR%
) else (
    echo   [OK] Archive created: %PACKAGE_DIR%_%TIMESTAMP%.zip
)

REM ========================================
REM Create GitHub Instructions
REM ========================================
echo.
echo Creating GitHub upload instructions...

(
echo # GitHub Upload Instructions
echo.
echo ## Files to Upload
echo.
echo 1. **ZIP Archive:** `%PACKAGE_DIR%_%TIMESTAMP%.zip`
echo    - This is the main distribution file
echo.
echo 2. **README:** Already included in the ZIP as README.md
echo.
echo ## GitHub Release Steps
echo.
echo ### Step 1: Create New Release
echo ```
echo 1. Go to your GitHub repository
echo 2. Click "Releases" ^> "Create a new release"
echo 3. Tag version: v1.0.0 ^(or appropriate version^)
echo 4. Release title: "RovoDev MCP Testing Package v1.0"
echo ```
echo.
echo ### Step 2: Release Description
echo Use this template:
echo.
echo ```markdown
echo # RovoDev MCP Testing Package
echo.
echo **6 Powerful MCP Servers for Enhanced AI Development**
echo.
echo ## What's Included
echo.
echo - 🧠 **Knowledge Database** - AI-powered code intelligence
echo - 🌐 **Unstoppable Browser** - Advanced web automation
echo - 📊 **Sandbox Monitor** - Intelligent process monitoring
echo - 👁️ **Vision Server** - Image analysis with AI
echo - 🔍 **Testing Server** - Automated code review
echo - 🤖 **Deep Learning Intelligence** - Semantic code search
echo.
echo ## Quick Start
echo.
echo 1. Download the ZIP file
echo 2. Extract to your `.rovodev` directory
echo 3. Run `INSTALL_MCP_TESTING.bat`
echo 4. Install AI models with `INSTALL_OLLAMA_MODELS.bat`
echo 5. Restart RovoDev
echo.
echo ## Requirements
echo.
echo - RovoDev installed
echo - Python 3.11+
echo - 25 GB disk space ^(for AI models^)
echo - 16 GB RAM minimum
echo.
echo ## Full Documentation
echo.
echo See README.md inside the package for complete installation and usage instructions.
echo ```
echo.
echo ### Step 3: Upload Files
echo ```
echo 1. Drag and drop the ZIP file to the release assets area
echo 2. Publish release
echo ```
echo.
echo ### Step 4: Update Repository README
echo Add this to your main README.md:
echo.
echo ```markdown
echo ## MCP Testing Package
echo.
echo Check out the [latest release](https://github.com/YOUR_USERNAME/YOUR_REPO/releases^) 
echo for the complete MCP testing package with 6 powerful AI-enhanced servers!
echo ```
echo.
echo ## Package Contents
echo.
echo - All 6 MCP server directories with dependencies
echo - Automated installation scripts
echo - Testing utilities
echo - Complete documentation
echo - Configuration examples
echo.
echo **Total package size:** ~50-100 MB ^(excluding AI models^)
echo **AI models ^(separate download^):** ~19 GB
echo.
) > "%PACKAGE_DIR%_GITHUB_INSTRUCTIONS.txt"

echo   [OK] GitHub instructions created

REM ========================================
REM Summary
REM ========================================
echo.
echo ========================================
echo  PACKAGE CREATION COMPLETE!
echo ========================================
echo.
echo Files created:
echo   1. Directory: %PACKAGE_DIR%\
echo   2. Archive:   %PACKAGE_DIR%_%TIMESTAMP%.zip
echo   3. Guide:     %PACKAGE_DIR%_GITHUB_INSTRUCTIONS.txt
echo.
echo What's included:
echo   - 6 MCP server directories
echo   - Installation scripts
echo   - Configuration files
echo   - Complete documentation
echo.
echo Next steps:
echo   1. Review the package in: %PACKAGE_DIR%\
echo   2. Test the installation locally
echo   3. Read: %PACKAGE_DIR%_GITHUB_INSTRUCTIONS.txt
echo   4. Upload to GitHub releases
echo.
echo ========================================
echo.
pause
