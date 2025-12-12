# Rex Unstoppable Browser MCP Server

**Unrestricted web browsing with anti-detection and Cloudflare bypass**

## Features

🔥 **Patchright-powered** - Undetectable browser automation  
🛡️ **Cloudflare bypass** - Integrated FlareSolverr approach  
🍪 **Session management** - Persistent logins and cookies  
📸 **Screenshots** - Capture pages and elements  
🎯 **Smart extraction** - CSS selector-based data scraping  
⚡ **JavaScript execution** - Run custom scripts on pages  
🚫 **No API limits** - Browse freely without restrictions

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements_unstoppable.txt
```

2. **Install Patchright browsers:**
```bash
patchright install chromium
```

3. **Move to MCP directory:**
```bash
# Copy this file to C:\Users\ggfuc\.rovodev\mcp_unstoppable_browser\server.py
```

## Configuration

Add to your RovoDev MCP config:

```json
{
  "mcpServers": {
    "rex-unstoppable-browser": {
      "command": "C:\\Users\\ggfuc\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": ["C:\\Users\\ggfuc\\.rovodev\\mcp_unstoppable_browser\\server.py"]
    }
  }
}
```

## Available Tools

### 1. `browse_url` - Navigate to any URL
```json
{
  "url": "https://example.com",
  "session_id": "default",
  "wait_for": ".content",
  "timeout": 30
}
```

### 2. `browse_interact` - Automate interactions
```json
{
  "session_id": "default",
  "actions": [
    {"type": "goto", "value": "https://example.com"},
    {"type": "fill", "selector": "#search", "value": "test"},
    {"type": "click", "selector": "button[type=submit]"},
    {"type": "wait", "value": 2000},
    {"type": "scroll"}
  ]
}
```

### 3. `browse_screenshot` - Capture page or element
```json
{
  "session_id": "default",
  "selector": ".main-content",
  "full_page": false
}
```

### 4. `browse_execute_js` - Run JavaScript
```json
{
  "session_id": "default",
  "script": "return document.title;"
}
```

### 5. `extract_data` - Scrape with selectors
```json
{
  "session_id": "default",
  "selectors": {
    "title": "h1",
    "links": "a.link"
  },
  "extract_all": true
}
```

### 6. `bypass_cloudflare` - Nuclear option for CF protection
```json
{
  "url": "https://cloudflare-protected-site.com",
  "max_timeout": 60000
}
```

### 7. Session Management
- `session_create` - Create new session
- `session_destroy` - Close session
- `get_cookies` - Export cookies
- `set_cookies` - Import cookies

## How It Works

1. **Normal browsing** → Uses Patchright (undetectable)
2. **Tough sites** → Patchright with stealth flags
3. **Cloudflare protected** → Falls back to FlareSolverr method

## Security Notes

- Bypasses most bot detection
- Looks like real Chrome browser
- Persistent sessions for logged-in sites
- Cookie export for use with other tools

## Boss's Notes

This is YOUR tool. No limits, no tracking, no bullshit.  
Browse anywhere, scrape anything, automate everything.

Built by Rex for the mission. 🔥
