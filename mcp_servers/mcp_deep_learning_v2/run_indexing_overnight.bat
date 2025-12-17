@echo off
title RovoDev Indexing - Running Overnight
color 0A
echo ================================================================================
echo ROVODEV CODEBASE INDEXING - OVERNIGHT RUN
echo ================================================================================
echo.
echo Started at: %date% %time%
echo This window will stay open all night.
echo.
echo Progress will be shown below...
echo ================================================================================
echo.

cd /d "%~dp0"
python reindex_codebase.py --force

echo.
echo ================================================================================
echo INDEXING COMPLETE!
echo Finished at: %date% %time%
echo ================================================================================
echo.
echo Press any key to close this window...
pause >nul
