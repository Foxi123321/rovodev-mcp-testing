@echo off
title Auto-Restart Indexing (Crash Protection)
color 0C
echo ================================================================================
echo CRASH PROTECTION - AUTO RESTART
echo ================================================================================
echo This will monitor and auto-restart indexing if it crashes.
echo Press Ctrl+C to stop monitoring.
echo ================================================================================
echo.

:LOOP
echo [%date% %time%] Checking if indexing is running...

tasklist /FI "WINDOWTITLE eq RovoDev Indexing - Running Overnight" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [%date% %time%] ✓ Indexing is running. Checking again in 5 minutes...
    timeout /t 300 /nobreak >nul
    goto LOOP
) else (
    echo [%date% %time%] ⚠ Indexing window NOT found!
    echo [%date% %time%] Checking if it completed successfully...
    
    if exist "%USERPROFILE%\.rovodev\deep_learning_v2\knowledge_new.db" (
        for %%A in ("%USERPROFILE%\.rovodev\deep_learning_v2\knowledge_new.db") do set size=%%~zA
        if !size! GTR 10000000 (
            echo [%date% %time%] ✓ Database is large - probably completed successfully!
            echo [%date% %time%] You can close this window.
            pause
            exit
        )
    )
    
    echo [%date% %time%] ❌ CRASH DETECTED! Restarting in 10 seconds...
    timeout /t 10 /nobreak
    
    echo [%date% %time%] Starting indexing again...
    start "RovoDev Indexing - Running Overnight" cmd /c "cd /d %~dp0 && run_indexing_overnight.bat"
    
    timeout /t 30 /nobreak
    goto LOOP
)
