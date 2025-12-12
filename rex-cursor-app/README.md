# Rex Cursor App

Cursor-style desktop application for Rex with automatic account rotation.

## Setup

```bash
cd rex-cursor-app
npm install
```

## Development

Make sure `rex_server_enhanced.py` is running on port 8000, then:

```bash
npm run dev
```

This will start:
- Vite dev server on port 5173
- Electron app with hot reload

## Build

```bash
npm run build
```

Creates a distributable desktop app in `dist/`.

## Features

- ⚡ Real-time chat with Rex
- 🔄 Auto-rotation status monitoring
- 🎨 Cursor-style 3-panel layout
- 📊 Live activity feed
- 💻 Desktop app (Electron)
- 🎯 Connects to existing rex_server_enhanced.py

## Architecture

```
Rex Cursor App (Electron + React)
    ↓
rex_server_enhanced.py (Port 8000)
    ↓
Rovo Dev Server (acli)
```
