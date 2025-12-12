# MCP Testing & Review Server

**Automated code review and browser testing for AI assistants (DeepSeek, Claude, etc.)**

---

## 🎯 What This Does

This MCP server gives AI models the ability to:
- **Review code** for bugs, security issues, and quality problems
- **Test websites** by opening browsers, clicking buttons, filling forms
- **Capture screenshots** of web pages
- **Detect errors** from console logs
- **Run JavaScript** in browser context

---

## 🔧 Setup

### 1. Install Dependencies
```bash
cd mcp_testing_server
pip install -r requirements.txt
playwright install chromium
```

### 2. Test the Server
```bash
python server.py
```

---

## 🚀 Available Tools

### Code Review Tools
- `review_code` - Analyze code files for issues

### Browser Automation Tools
- `browser_navigate` - Open a URL
- `browser_click` - Click elements
- `browser_fill` - Fill input fields
- `browser_screenshot` - Capture page screenshots
- `browser_get_errors` - Get console errors
- `browser_execute_js` - Run JavaScript
- `browser_close` - Close browser

---

## 📦 Integration with RovoDev

Add this to your RovoDev MCP config:

```json
{
  "mcpServers": {
    "testing-review": {
      "command": "python",
      "args": ["C:/path/to/mcp_testing_server/server.py"]
    }
  }
}
```

---

## 🤖 Using with DeepSeek (Ollama)

DeepSeek can use these tools to:
1. Review code RovoDev writes
2. Test websites/apps automatically
3. Report bugs and issues back

---

## 📁 File Structure

```
mcp_testing_server/
├── server.py              # Main MCP server
├── config.json            # Configuration
├── requirements.txt       # Dependencies
├── tools/
│   ├── code_reviewer.py   # Code analysis
│   ├── browser_tester.py  # Playwright automation
│   └── app_tester.py      # Desktop testing (future)
└── screenshots/           # Captured screenshots
```

---

## ⚙️ Configuration

Edit `config.json` to customize:
- Browser headless mode
- Screenshot settings
- Timeout values
- Review strictness
