# 🚀 Rex Cursor App - Installation Guide

## Prerequisites

1. **Node.js** (v18 or higher)
   - Download: https://nodejs.org/
   - Check version: `node --version`

2. **npm** (comes with Node.js)
   - Check version: `npm --version`

3. **Rex Server** (already installed)
   - Located at: `C:\Users\ggfuc\.rovodev\`
   - `rex_server_enhanced.py` with 11 accounts

---

## Installation Steps

### 1. Navigate to App Directory

```bash
cd C:\Users\ggfuc\.rovodev\rex-cursor-app
```

### 2. Install Dependencies

```bash
npm install
```

This will install:
- React + TypeScript
- Electron
- Tailwind CSS
- Monaco Editor
- All other dependencies

**Note:** This may take 2-3 minutes on first install.

---

## Running the App

### Development Mode (Recommended for testing)

**Step 1: Start Rex Server**

In one terminal:
```bash
cd C:\Users\ggfuc\.rovodev
python rex_server_enhanced.py 8000
```

**Step 2: Start Cursor App**

In another terminal:
```bash
cd C:\Users\ggfuc\.rovodev\rex-cursor-app
npm run dev
```

The Electron app will open automatically with hot reload enabled!

---

## Building Desktop App

To create a standalone `.exe`:

```bash
npm run build
```

The installer will be in `dist/` folder.

---

## Quick Launch Script

We'll create a batch file to launch everything:

**File: `launch_rex_cursor_desktop.bat`**

```batch
@echo off
echo Starting Rex Cursor Desktop App...
cd /d C:\Users\ggfuc\.rovodev

REM Start server
start "Rex Server" cmd /k python rex_server_enhanced.py 8000

REM Wait for server
timeout /t 5 /nobreak

REM Start Electron app
cd rex-cursor-app
start "Rex Cursor App" cmd /k npm run dev

echo.
echo Both server and app starting...
echo Close this window anytime.
pause
```

---

## Troubleshooting

### "npm not found"
- Install Node.js from https://nodejs.org/
- Restart terminal after installing

### "Module not found" errors
- Run `npm install` again
- Delete `node_modules` folder and run `npm install`

### App won't connect to server
- Make sure `rex_server_enhanced.py` is running on port 8000
- Check server logs for errors
- Try: `netstat -ano | findstr :8000`

### Electron won't start
- Run `npm run dev:vite` first to check if Vite works
- Check Node.js version: `node --version` (should be v18+)

---

## What You Get

✅ **3-Panel Cursor-Style Layout**
- Left: Chat history & file tree
- Center: Chat interface with streaming
- Right: Live activity feed

✅ **Real-Time Features**
- Streaming responses from Rex
- Auto-rotation notifications
- Account status monitoring
- Tool execution visibility

✅ **Desktop App**
- Native window
- System tray integration (coming)
- Keyboard shortcuts
- Dark theme

---

## Next Steps After Install

1. Run `npm install`
2. Test with `npm run dev`
3. If working, use the launch script
4. Build `.exe` with `npm run build` when ready

**Boss, ready to install!** 🔥
