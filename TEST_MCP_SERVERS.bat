@echo off
REM ========================================
REM MCP SERVERS TEST SUITE
REM ========================================
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  MCP SERVERS TEST SUITE
echo ========================================
echo.
echo Testing all 6 MCP servers...
echo.

set OLLAMA_BASE_URL=http://localhost:11434
set PASSED=0
set FAILED=0

REM ========================================
REM TEST 1: Knowledge Database
REM ========================================
echo [1/6] Testing Knowledge Database...
cd mcp_knowledge_db 2>nul || (
    echo   [FAIL] Directory not found
    set /a FAILED+=1
    goto test2
)

REM Quick syntax check
python -c "import server" 2>nul
if errorlevel 1 (
    echo   [FAIL] Import error
    set /a FAILED+=1
) else (
    echo   [PASS] Knowledge Database OK
    set /a PASSED+=1
)
cd ..

:test2
REM ========================================
REM TEST 2: Unstoppable Browser
REM ========================================
echo [2/6] Testing Unstoppable Browser...
cd mcp_unstoppable_browser 2>nul || (
    echo   [FAIL] Directory not found
    set /a FAILED+=1
    goto test3
)

python -c "import server" 2>nul
if errorlevel 1 (
    echo   [FAIL] Import error
    set /a FAILED+=1
) else (
    echo   [PASS] Unstoppable Browser OK
    set /a PASSED+=1
)
cd ..

:test3
REM ========================================
REM TEST 3: Sandbox Monitor
REM ========================================
echo [3/6] Testing Sandbox Monitor...
cd mcp_sandbox_monitor 2>nul || (
    echo   [FAIL] Directory not found
    set /a FAILED+=1
    goto test4
)

python -c "import server" 2>nul
if errorlevel 1 (
    echo   [FAIL] Import error
    set /a FAILED+=1
) else (
    echo   [PASS] Sandbox Monitor OK
    set /a PASSED+=1
)
cd ..

:test4
REM ========================================
REM TEST 4: Vision Server
REM ========================================
echo [4/6] Testing Vision Server...
cd mcp_vision_simple 2>nul || (
    echo   [FAIL] Directory not found
    set /a FAILED+=1
    goto test5
)

python -c "import server" 2>nul
if errorlevel 1 (
    echo   [FAIL] Import error
    set /a FAILED+=1
) else (
    echo   [PASS] Vision Server OK
    set /a PASSED+=1
)
cd ..

:test5
REM ========================================
REM TEST 5: Testing Server
REM ========================================
echo [5/6] Testing Testing Server...
cd mcp_testing_server 2>nul || (
    echo   [FAIL] Directory not found
    set /a FAILED+=1
    goto test6
)

python -c "import server" 2>nul
if errorlevel 1 (
    echo   [FAIL] Import error
    set /a FAILED+=1
) else (
    echo   [PASS] Testing Server OK
    set /a PASSED+=1
)
cd ..

:test6
REM ========================================
REM TEST 6: Deep Learning Intelligence
REM ========================================
echo [6/6] Testing Deep Learning Intelligence...
cd mcp_deep_learning_v2 2>nul || (
    echo   [FAIL] Directory not found
    set /a FAILED+=1
    goto results
)

set PYTHONPATH=%CD%
python -c "import server" 2>nul
if errorlevel 1 (
    echo   [FAIL] Import error
    set /a FAILED+=1
) else (
    echo   [PASS] Deep Learning Intelligence OK
    set /a PASSED+=1
)
cd ..

:results
REM ========================================
REM TEST RESULTS
REM ========================================
echo.
echo ========================================
echo  TEST RESULTS
echo ========================================
echo.
echo   Passed: %PASSED%/6
echo   Failed: %FAILED%/6
echo.

if %FAILED% GTR 0 (
    echo [WARNING] Some tests failed!
    echo.
    echo Troubleshooting:
    echo   1. Re-run INSTALL_MCP_TESTING.bat
    echo   2. Check that all directories exist
    echo   3. Verify Python dependencies installed
    echo.
) else (
    echo [SUCCESS] All servers ready!
    echo.
    echo Next steps:
    echo   1. Make sure Ollama is installed
    echo   2. Run INSTALL_OLLAMA_MODELS.bat
    echo   3. Restart RovoDev
    echo.
)

echo ========================================
echo.
pause
