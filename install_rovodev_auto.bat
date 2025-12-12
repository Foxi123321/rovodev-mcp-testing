@echo off
cls
echo ========================================
echo   INSTALL ROVODEV AUTO COMMAND
echo ========================================
echo.

REM Get current directory
set INSTALL_DIR=%~dp0

echo Creating rovodev-auto launcher script...
echo.

REM Create the launcher script
(
echo @echo off
echo REM RovoDev Auto - Starts Ollama + MCP Testing Server + RovoDev
echo.
echo REM Set MCP config
echo set ROVODEV_MCP_CONFIG=%INSTALL_DIR%mcp_testing_config.json
echo.
echo REM Start Ollama
echo start /B ollama serve ^>nul 2^>^&1
echo timeout /t 2 /nobreak ^>nul
echo.
echo REM Start MCP Testing Server
echo start "MCP Testing Server" /MIN cmd /c "cd /d %INSTALL_DIR%mcp_testing_server && python server.py"
echo timeout /t 2 /nobreak ^>nul
echo.
echo REM Launch RovoDev
echo acli rovodev run
) > "%TEMP%\rovodev-auto.bat"

echo Installing to system PATH...
echo.

REM Create a directory in user profile for custom commands
set COMMANDS_DIR=%USERPROFILE%\.rovodev\bin
if not exist "%COMMANDS_DIR%" mkdir "%COMMANDS_DIR%"

REM Copy the launcher there
copy "%TEMP%\rovodev-auto.bat" "%COMMANDS_DIR%\rovodev-auto.bat" >nul

echo Adding to PATH...
echo.

REM Add to user PATH if not already there
set "NEWPATH=%COMMANDS_DIR%"
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH 2^>nul') do set "CURRENTPATH=%%b"

echo %CURRENTPATH% | find /i "%COMMANDS_DIR%" >nul
if errorlevel 1 (
    setx PATH "%CURRENTPATH%;%NEWPATH%" >nul
    echo    ✅ Added to PATH
) else (
    echo    ✅ Already in PATH
)

echo.
echo ========================================
echo   ✅ INSTALLATION COMPLETE!
echo ========================================
echo.
echo Installed: %COMMANDS_DIR%\rovodev-auto.bat
echo.
echo ⚠️  IMPORTANT: Close this PowerShell window and open a NEW one!
echo.
echo Then you can use:
echo.
echo    rovodev-auto
echo.
echo This will start:
echo    • Ollama
echo    • MCP Testing Server
echo    • RovoDev with MCP enabled
echo.
echo 🎯 All in one command!
echo.
pause
