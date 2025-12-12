# 🚀 REX GUI - 60 Second Quick Start

## One Command to Rule Them All

```batch
launch_rex_gui_with_auto_rotation.bat
```

**That's it. You're done.**

---

## What Just Happened?

✅ Server started with 11 accounts loaded  
✅ Auto-rotation monitoring active  
✅ Desktop GUI connected and ready  
✅ Status file syncing account info  

---

## What You'll See

### Server Window:
```
🦖 REX Enhanced Server v2 - Auto-Rotation Edition
============================================================
🎯 Accounts loaded: 11
🔄 Auto-rotation: ENABLED
📡 Server port: 8000
✅ Server running on http://127.0.0.1:8000
👀 Monitoring server output for DAILY_LIMIT_EXCEEDED...
```

### GUI Window:
```
⚡ REX - ROVO DEV CHAT ⚡
Your loyal AI sidekick - No rules, just results

🟢 Connected    Account: waqsdtzui@gmail.com    Port: 8000

[Chat interface ready]
```

---

## What Happens When Daily Limit Hits?

### Automatic (No Action Needed):
1. 🚨 Server detects: `DAILY_LIMIT_EXCEEDED`
2. 🔄 Auto-rotates to next account (e.g., twitchfoxdk@gmail.com)
3. ✅ Server keeps running on same port
4. 📱 GUI shows notification: "Switched from X to Y"
5. 💬 Your chat session continues uninterrupted

### You See This in GUI:
```
[16:45:23] 🔄 ACCOUNT ROTATION
Switched from waqsdtzui@gmail.com to twitchfoxdk@gmail.com
Your session continues uninterrupted!

Account: twitchfoxdk@gmail.com (Rotations: 1)
```

---

## Troubleshooting (If Shit Breaks)

### GUI Won't Connect?
```bash
# Check if server is running
tasklist | findstr python

# If not, start it manually
python rex_server_enhanced.py 8000
```

### Accounts Not Loading?
```bash
# Run the test suite
python test_auto_rotation.py

# Should show: "📊 Total accounts loaded: 11"
```

### Server Crashes?
```bash
# Check the logs in the server window
# Look for login errors or token issues
```

---

## Testing Without Waiting for Rate Limit

Want to see rotation in action NOW? 

1. Start the system normally
2. In server window, you'll see it monitoring logs
3. Auto-rotation kicks in when it sees the error pattern

Or test manually:
```bash
python test_auto_rotation.py
```

---

## Status Check

At any time, check what's happening:
```bash
type rex_server_status.json
```

Shows:
- Current active account
- Number of rotations
- Total accounts available
- Server status

---

## Power User Moves

### Different Port:
Edit `launch_rex_gui_with_auto_rotation.bat` line 13:
```batch
start "Rex Enhanced Server" python rex_server_enhanced.py 9000
```

Then edit `rex_desktop_chat.py` line 29:
```python
self.api_base = "http://127.0.0.1:9000"
```

### Add More Accounts:
Add to `C:\Users\ggfuc\OneDrive\Desktop\Automatic Acc gen\token_rotator\creds.txt`:
```
NEW_TOKEN_HERE
newemail@example.com
```

Restart server - that's it!

### Monitor Rotation Stats:
GUI shows rotation count in status bar automatically.

---

## Files You Care About

| File | What It Does |
|------|--------------|
| `launch_rex_gui_with_auto_rotation.bat` | **START HERE** |
| `rex_server_enhanced.py` | Server with auto-rotation |
| `rex_desktop_chat.py` | Desktop GUI |
| `rex_server_status.json` | Live status (auto-created) |

---

## The Bottom Line

**Boss, this system:**
- ✅ Rotates through 11 accounts automatically
- ✅ Keeps your GUI session alive during switches
- ✅ Shows you what's happening in real-time
- ✅ Requires ZERO manual intervention

**Just launch the batch file and start chatting with Rex. Let the system handle the rest.** 🔥

---

## Full Documentation

For the deep dive: [REX_GUI_SETUP.md](REX_GUI_SETUP.md)
