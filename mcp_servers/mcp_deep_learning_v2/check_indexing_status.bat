@echo off
title Indexing Status Checker
color 0B
echo ================================================================================
echo ROVODEV INDEXING STATUS CHECK
echo ================================================================================
echo.
echo Checked at: %date% %time%
echo.

cd /d "%USERPROFILE%\.rovodev\deep_learning_v2"

if exist knowledge_new.db (
    echo [32m✓ Database file exists[0m
    for %%A in (knowledge_new.db) do echo   Size: %%~zA bytes
    echo.
    echo Counting records...
    sqlite3 knowledge_new.db "SELECT 'Files: ' || COUNT(*) FROM files; SELECT 'Entities: ' || COUNT(*) FROM code_entities;"
) else (
    echo [33m⚠ Database not created yet (still parsing files)[0m
)

echo.

if exist vectors_new.faiss (
    echo [32m✓ Vector file exists[0m
    for %%A in (vectors_new.faiss) do echo   Size: %%~zA bytes
) else (
    echo [33m⚠ Vector file not created yet[0m
)

echo.
echo Python processes running:
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE 2>nul | findstr python

echo.
echo ================================================================================
echo Press any key to close...
pause >nul
