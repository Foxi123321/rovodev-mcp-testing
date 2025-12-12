@echo off
REM Launch Rex GUI with Auto-Rotation Server
REM Boss, this is your one-click solution!

echo.
echo ====================================
echo  REX GUI + AUTO-ROTATION LAUNCHER
echo ====================================
echo.
echo Starting Rex with personality mode...
echo - 11 accounts loaded
echo - Auto-rotation enabled
echo - Rex personality active
echo.

REM Start the enhanced server in a new window that stays open
start "Rex Enhanced Server" cmd /k python rex_server_enhanced.py 8000

REM Wait longer for server to fully start
echo Waiting for server to initialize...
timeout /t 8 /nobreak > nul

echo.
echo Server should be ready... launching GUI now...
timeout /t 1 /nobreak > nul

REM Launch the GUI
start "Rex Desktop Chat" python rex_desktop_chat.py

echo.
echo ====================================
echo  Both server and GUI launched!
echo ====================================
echo.
echo Server will AUTO-ROTATE when daily limit hits.
echo Your GUI will stay connected - no interruptions!
echo.
echo [LAUNCHER WINDOW]
echo - Server running in separate window (check taskbar)
echo - GUI running in separate window
echo - Both windows will stay open
echo.
echo You can close THIS window safely now.
echo The server and GUI will keep running!
echo.
pause
