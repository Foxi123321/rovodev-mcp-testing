@echo off
cls
echo ========================================
echo   CREATE ROVODEV MCP TESTING PACKAGE
echo ========================================
echo.

REM Set paths
set SOURCE_DIR=%~dp0
set PACKAGE_NAME=RovoDev_MCP_Testing_Package
set PACKAGE_DIR=%SOURCE_DIR%%PACKAGE_NAME%

echo Creating package for your friend...
echo.

REM Create package directory
if exist "%PACKAGE_DIR%" (
    echo Removing old package...
    rmdir /s /q "%PACKAGE_DIR%"
)

mkdir "%PACKAGE_DIR%"

echo [1/6] Copying MCP Testing Server...
xcopy "%SOURCE_DIR%mcp_testing_server" "%PACKAGE_DIR%\mcp_testing_server\" /E /I /Y >nul
echo    ✅ MCP server copied

echo [2/6] Copying configuration files...
copy "%SOURCE_DIR%mcp.json" "%PACKAGE_DIR%\" >nul
copy "%SOURCE_DIR%config.yml" "%PACKAGE_DIR%\" >nul
echo    ✅ Configs copied

echo [3/6] Copying installation script...
copy "%SOURCE_DIR%INSTALL.bat" "%PACKAGE_DIR%\" >nul
echo    ✅ Installer copied

echo [4/6] Copying documentation...
copy "%SOURCE_DIR%ROVODEV_MCP_TESTING_PACKAGE_README.md" "%PACKAGE_DIR%\README.md" >nul
copy "%SOURCE_DIR%mcp_testing_server\README.md" "%PACKAGE_DIR%\MCP_SERVER_DETAILS.md" >nul
echo    ✅ Docs copied

echo [5/6] Creating quick start guide...
(
echo ========================================
echo   QUICK START
echo ========================================
echo.
echo 1. Extract this folder to: C:\Users\YOUR_USERNAME\.rovodev\
echo.
echo 2. Run: INSTALL.bat
echo.
echo 3. Start RovoDev: acli rovodev run
echo.
echo 4. Ask it: "Build me a calculator app"
echo.
echo 5. Watch it automatically build, test, and fix!
echo.
echo Read README.md for full documentation.
echo.
) > "%PACKAGE_DIR%\QUICK_START.txt"
echo    ✅ Quick start created

echo [6/6] Creating ZIP file...
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%SOURCE_DIR%%PACKAGE_NAME%.zip' -Force"
if errorlevel 1 (
    echo    ⚠️  Could not create ZIP automatically
    echo    Please manually ZIP the folder: %PACKAGE_DIR%
) else (
    echo    ✅ ZIP created: %PACKAGE_NAME%.zip
)

echo.
echo ========================================
echo   ✅ PACKAGE READY!
echo ========================================
echo.
echo Package location:
echo   %PACKAGE_NAME%.zip
echo.
echo File size: 
powershell -Command "(Get-Item '%SOURCE_DIR%%PACKAGE_NAME%.zip').Length / 1MB | ForEach-Object { '{0:N2} MB' -f $_ }"
echo.
echo Send this ZIP to your friend!
echo.
echo They need to:
echo   1. Extract to C:\Users\THEIR_USERNAME\.rovodev\
echo   2. Run INSTALL.bat
echo   3. Start using RovoDev with auto-testing!
echo.
pause
