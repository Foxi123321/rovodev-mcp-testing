# 🧪 Testing Sandbox Monitor with RovoDev

## ✅ Configuration Added!

The sandbox-monitor is now in your `mcp.json` as the 8th MCP server.

## 🚀 Test Commands for Rex

### Test 1: List Available Tools
```
Rex, what tools are available in the sandbox-monitor?
```

Expected: Rex should list all 10 tools.

### Test 2: Launch a Simple Test
```
Rex, use sandbox-monitor to launch this PowerShell script:
Write-Host 'Test started'
$answer = Read-Host 'Continue? (Y/N)'
Write-Host "You chose: $answer"
```

Expected: Rex launches the script, detects it's waiting, and can send input.

### Test 3: Check for Stuck Processes
```
Rex, check if there are any stuck processes using sandbox-monitor
```

Expected: Rex shows any PowerShell processes waiting for input.

### Test 4: Full Autonomous Test
```
Rex, start the sandbox-monitor background daemon, then launch a test script that asks for confirmation, and monitor it automatically
```

Expected: Rex starts monitoring, launches script, auto-detects stuck, and responds.

### Test 5: Knowledge Search
```
Rex, search the sandbox-monitor knowledge database for "input" or "confirmation"
```

Expected: Rex shows past decisions from our tests.

## 📊 Expected Behavior

1. **Rex recognizes the tools** - Shows all 10 sandbox-monitor tools
2. **Can launch processes** - Creates visible PowerShell window
3. **Detects stuck behavior** - Identifies waiting processes
4. **Sends input** - Types into the waiting window
5. **Logs decisions** - Stores in knowledge DB

## 🐛 Troubleshooting

If Rex doesn't see the tools:
1. Restart RovoDev completely
2. Check logs for MCP server startup
3. Verify Python path is correct
4. Run `python C:\Users\ggfuc\.rovodev\mcp_sandbox_monitor\server.py` manually to test

If tools fail:
1. Check if Ollama is running (for AI decisions)
2. Verify pyautogui is installed: `pip install pyautogui pygetwindow`
3. Run the test: `python test_mcp_server.py`

## 🎯 Success Criteria

✅ Rex lists sandbox-monitor tools
✅ Rex can launch monitored processes
✅ Rex detects stuck processes
✅ Rex sends keyboard input successfully
✅ Decisions are logged to knowledge DB

---

**Ready to test!** Start RovoDev and try the commands above. 🚀
