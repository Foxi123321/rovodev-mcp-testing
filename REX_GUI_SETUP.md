# 🦖 REX GUI with Auto-Rotation - Complete Setup Guide

Your loyal AI assistant with **automatic account rotation** and a slick desktop GUI. No interruptions, no manual switching, just pure productivity.

---

## 🎯 What This Does

- **Desktop GUI**: Dark-themed chat interface for Rovo Dev (no browser, no CORS issues)
- **Auto-Rotation**: Automatically switches accounts when daily limits hit
- **Seamless Experience**: GUI stays connected during rotations - you won't even notice
- **11 Accounts Ready**: Loaded and ready to cycle through automatically
- **Real-time Status**: See which account is active and how many rotations happened

---

## ⚡ Quick Start (One-Click Launch)

### Windows:
```batch
launch_rex_gui_with_auto_rotation.bat
```

That's it! The batch file will:
1. Start the enhanced server with auto-rotation (port 8000)
2. Wait 3 seconds for server startup
3. Launch the desktop GUI
4. Connect everything automatically

---

## 📋 Prerequisites

### 1. Accounts Setup
- **Location**: `C:\Users\ggfuc\OneDrive\Desktop\Automatic Acc gen\token_rotator\creds.txt`
- **Format**: Token on one line, email on next line (repeat)
- **Current Status**: ✅ 11 accounts loaded and ready

Example `creds.txt`:
```
ATATT3xFfGF0JFYtKTOq...=B8D74AB1
waqsdtzui@gmail.com
ATATT3xFfGF0fgycc2iB...=725A21D3
twitchfoxdk@gmail.com
```

### 2. Python Dependencies
```bash
pip install requests tkinter
```

### 3. Atlassian CLI
- **Path**: `C:\Users\ggfuc\.local\share\acli\1.3.4-stable\plugin\rovodev\atlassian_cli_rovodev.exe`
- Should be already installed and working

---

## 🚀 Manual Launch (If You Want Control)

### Step 1: Start Enhanced Server
```bash
python rex_server_enhanced.py 8000
```

This will:
- Load all 11 accounts
- Login with the first account
- Start Rovo Dev server on port 8000
- Monitor for `DAILY_LIMIT_EXCEEDED` errors
- Auto-rotate when limits hit

### Step 2: Launch GUI
```bash
python rex_desktop_chat.py
```

This will:
- Open the desktop chat interface
- Connect to server at `http://127.0.0.1:8000`
- Monitor account status in real-time
- Show notifications when accounts rotate

---

## 🔥 How Auto-Rotation Works

### The Flow:
1. **Server monitors output** from Rovo Dev subprocess
2. **Detects errors** matching patterns like:
   - `DAILY_LIMIT_EXCEEDED`
   - `status_code: 429`
   - `dailyRemaining: 0`
3. **Auto-rotates** to next account:
   - Logs out from current account
   - Logs in with next account (cycles through 11 accounts)
   - Updates status file (`rex_server_status.json`)
4. **GUI stays connected** - no interruption!
5. **Shows notification** in chat: "Switched from X to Y"

### Status File Communication:
- Server writes to: `rex_server_status.json`
- GUI reads from: `rex_server_status.json`
- Updates every 2 seconds

Example status file:
```json
{
  "current_account": "waqsdtzui@gmail.com",
  "rotation_count": 2,
  "total_accounts": 11,
  "server_port": 8000,
  "status": "running",
  "last_updated": 1638230415.234
}
```

---

## 🖥️ Using the GUI

### Interface:
- **Header**: Shows Rex branding and tagline
- **Status Bar**: 
  - 🟢 Connection status (Green = Connected)
  - Current account email
  - Rotation count (if any)
  - Port number
  - Spoofer status (if enabled)
- **Chat Area**: Dark terminal-style interface
  - Green text = Rex (assistant)
  - Red text = You (user)
  - Orange text = System messages
  - Red text = Errors
- **Input Area**: Type your message, press Enter (or click SEND)

### Keyboard Shortcuts:
- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Ctrl+C**: Close GUI

### Features:
- **Streaming responses**: See Rex's reply as it's generated
- **Session management**: Each GUI launch creates a fresh session
- **Error handling**: Clear error messages if server disconnects
- **Auto-scroll**: Chat always shows latest messages

---

## 🧪 Testing the Setup

### Test 1: Verify Accounts Loaded
```bash
python test_auto_rotation.py
```

Expected output:
```
🦖 REX AUTO-ROTATION TEST SUITE
============================================================
🧪 TEST 1: Error Detection
✅ All error patterns detected correctly

🧪 TEST 2: Account Loading
📊 Total accounts loaded: 11
📧 Current account: waqsdtzui@gmail.com

🧪 TEST 3: Rotation Simulation
✅ Error pattern detected! Rotation would be triggered.
```

### Test 2: Manual Server Test
```bash
python rex_server_enhanced.py 8000
```

Check logs for:
- ✅ `Loaded 11 accounts`
- ✅ `Successfully logged in as [email]`
- ✅ `Server running on http://127.0.0.1:8000`
- ✅ `Monitoring server output for DAILY_LIMIT_EXCEEDED...`

### Test 3: GUI Connection Test
1. Start server (test 2 above)
2. Launch GUI: `python rex_desktop_chat.py`
3. Check status bar shows: 🟢 Connected
4. Send a test message: "yo rex, you alive?"
5. Should get a response from Rex

---

## 🔧 Troubleshooting

### Problem: "No accounts loaded"
**Solution**: Check creds file exists and has correct format
```bash
# Verify file exists
dir "C:\Users\ggfuc\OneDrive\Desktop\Automatic Acc gen\token_rotator\creds.txt"

# Check first 4 lines
type "C:\Users\ggfuc\OneDrive\Desktop\Automatic Acc gen\token_rotator\creds.txt" | more
```

### Problem: GUI shows "🔴 Disconnected"
**Solution**: Make sure server is running
```bash
# Check if server process is running
tasklist | findstr python

# Start server if not running
python rex_server_enhanced.py 8000
```

### Problem: "Login failed" errors
**Solution**: Tokens might be expired
- Generate fresh tokens for accounts
- Update `creds.txt` with new tokens
- Restart server

### Problem: Server crashes on rotation
**Solution**: Check rotation interval
- Default: 10 seconds between rotations
- Increase if needed in `auto_rotation_handler.py`:
  ```python
  self.min_rotation_interval = 30  # Increase to 30 seconds
  ```

### Problem: Status file not updating
**Solution**: Check file permissions
```bash
# Try creating the file manually
echo {} > rex_server_status.json

# Check if file is readable
type rex_server_status.json
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    REX SYSTEM                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌──────────────────┐     │
│  │  rex_desktop_   │◄────────│ rex_server_      │     │
│  │  chat.py        │  HTTP   │ enhanced.py      │     │
│  │  (GUI)          │  8000   │ (Server Wrapper) │     │
│  └─────────────────┘         └──────────────────┘     │
│         │                             │                │
│         │ Reads                       │ Writes         │
│         ▼                             ▼                │
│  ┌──────────────────────────────────────────────┐     │
│  │     rex_server_status.json                   │     │
│  │  {current_account, rotation_count, ...}      │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │    auto_rotation_handler.py                  │     │
│  │  - Monitors for DAILY_LIMIT_EXCEEDED         │     │
│  │  - Triggers rotation on error detection      │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                   │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────┐     │
│  │    token_rotator.py                          │     │
│  │  - Manages 11 accounts                       │     │
│  │  - Handles login/logout via acli             │     │
│  │  - Cycles through accounts                   │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                   │
│                     ▼                                   │
│  ┌──────────────────────────────────────────────┐     │
│  │    Atlassian CLI (rovodev)                   │     │
│  │  - Actual Rovo Dev server subprocess         │     │
│  │  - Serves API on port 8000                   │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `rex_server_enhanced.py` | Main server with auto-rotation logic |
| `rex_desktop_chat.py` | Desktop GUI (Tkinter-based) |
| `auto_rotation_handler.py` | Detects errors and triggers rotations |
| `token_rotator.py` | Manages multiple accounts and switches between them |
| `launch_rex_gui_with_auto_rotation.bat` | One-click launcher |
| `test_auto_rotation.py` | Test suite for rotation system |
| `rex_server_status.json` | Real-time status (created at runtime) |
| `creds.txt` | Account tokens and emails |

---

## 🎮 Advanced Usage

### Custom Port:
```bash
python rex_server_enhanced.py 9000
python rex_desktop_chat.py  # Edit line 29 to change port
```

### Custom Creds File:
```bash
python rex_server_enhanced.py 8000 "path/to/my/creds.txt"
```

### Check Rotation Stats:
While server is running, the status file shows live stats:
```bash
type rex_server_status.json
```

### Monitor Server Logs:
Server outputs detailed logs including:
- Account rotations
- Error detections
- Login/logout events
- API requests

---

## 🔒 Security Notes

- **Tokens**: Keep `creds.txt` secure - it contains auth tokens
- **Status File**: Contains current account email but no tokens
- **Local Only**: Server binds to `127.0.0.1` (localhost only)
- **No Browser**: GUI doesn't expose anything via browser

---

## 💡 Pro Tips

1. **Keep GUI Open**: Let auto-rotation do its thing in the background
2. **Watch for Notifications**: GUI shows when accounts switch
3. **Monitor Rotation Count**: If it's high, you might be hitting limits fast
4. **Clean Logs**: Check server output if something seems off
5. **Fresh Sessions**: Each GUI launch creates a new session for clean state

---

## 🆘 Getting Help

If shit hits the fan:

1. **Check Server Logs**: Look for ERROR or WARNING messages
2. **Run Test Suite**: `python test_auto_rotation.py`
3. **Verify Accounts**: Make sure tokens are valid
4. **Check Status File**: See what state the system thinks it's in
5. **Restart Everything**: Close GUI, kill server, run batch file again

---

## 🎉 You're All Set!

**Boss, you're ready to roll. Just run:**
```batch
launch_rex_gui_with_auto_rotation.bat
```

**The system will:**
- ✅ Auto-rotate through 11 accounts
- ✅ Keep your GUI session alive
- ✅ Show you which account is active
- ✅ Notify you when switches happen
- ✅ Handle rate limits like a boss

**No manual intervention needed. Just chat with Rex and let the magic happen!** 🔥
