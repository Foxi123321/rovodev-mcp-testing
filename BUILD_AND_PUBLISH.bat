@echo off
cls
echo ========================================
echo   BUILD EVERYTHING AND PUBLISH
echo ========================================
echo.

cd /d "%USERPROFILE%\.rovodev"

echo [1/4] Creating package ZIP...
echo.
call CREATE_PACKAGE_FOR_FRIEND.bat

if not exist "RovoDev_MCP_Testing_Package.zip" (
    echo ❌ Package ZIP was not created!
    pause
    exit /b 1
)

echo    ✅ Package ZIP created: RovoDev_MCP_Testing_Package.zip
echo.

echo [2/4] Building installer EXE...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo    Installing PyInstaller...
    pip install pyinstaller
)

echo    Building installer (this may take 2-3 minutes)...
python build_installer_exe.py

if not exist "dist\RovoDev-MCP-Installer.exe" (
    echo    ⚠️  Installer EXE was not created (this is okay, we'll upload the ZIP)
) else (
    echo    ✅ Installer EXE created: dist\RovoDev-MCP-Installer.exe
)

echo.
echo [3/4] Publishing to GitHub...
echo.

call AUTO_PUBLISH_GITHUB_V2.bat

echo.
echo [4/4] Uploading installer EXE to release (if it exists)...
echo.

if exist "dist\RovoDev-MCP-Installer.exe" (
    gh release upload v1.0.0 "dist\RovoDev-MCP-Installer.exe" --clobber
    echo    ✅ Installer EXE uploaded to release
) else (
    echo    ⚠️  No installer EXE to upload (users will use the ZIP)
)

echo.
echo ========================================
echo   ✅ COMPLETE!
echo ========================================
echo.
echo Your release has:
if exist "dist\RovoDev-MCP-Installer.exe" (
    echo   ✅ RovoDev_MCP_Testing_Package.zip
    echo   ✅ RovoDev-MCP-Installer.exe
) else (
    echo   ✅ RovoDev_MCP_Testing_Package.zip
)
echo.
echo Opening your release page...
start https://github.com/ggfuc/rovodev-mcp-testing/releases/tag/v1.0.0
echo.
pause
