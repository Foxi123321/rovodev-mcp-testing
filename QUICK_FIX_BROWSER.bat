@echo off
cd /d "%USERPROFILE%\.rovodev"
git add mcp_testing_server/tools/browser_tester.py
git commit -m "fix: Browser auto-initializes on navigate"
git push
echo ✅ Browser fix pushed!
pause
