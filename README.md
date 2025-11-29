# 🔥 RovoDev MCP Testing Server

**Automated AI-powered code review, browser testing, and visual analysis for Atlassian RovoDev CLI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Required-green.svg)](https://ollama.com)

> Transform RovoDev from a code generator into a fully autonomous development system with automated testing, browser automation, and AI-powered visual analysis.

---

## 🎯 What This Does

Adds powerful automated testing capabilities to RovoDev:

- **🔍 Code Review** - Static analysis for bugs, security issues, and code smells
- **🌐 Browser Automation** - Automated testing with Patchright (undetectable)
- **📸 Screenshot Analysis** - LLaVA vision AI analyzes UI/UX
- **🤖 Auto-Testing** - RovoDev automatically tests everything it builds
- **💯 Local & Free** - No API costs, unlimited usage, 100% private

---

## 🚀 Quick Start

### Prerequisites

- [Atlassian RovoDev CLI](https://developer.atlassian.com/cloud/acli/guides/install-acli/) installed
- [Ollama](https://ollama.com) installed
- Python 3.8+ with pip

### Installation (Windows)

**Option 1: Auto-Installer (Recommended)**

1. Download [RovoDev-MCP-Installer.exe](https://github.com/YOUR_USERNAME/rovodev-mcp-testing/releases)
2. Run the installer
3. Start RovoDev: `acli rovodev run`

**Option 2: Manual Installation**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rovodev-mcp-testing.git
cd rovodev-mcp-testing

# Run the setup script
setup.bat

# Start RovoDev
acli rovodev run
```

---

## 📖 Usage

Once installed, RovoDev automatically tests everything it builds!

### Example

```
> "Build me a todo list app"
```

**RovoDev will:**
1. ✅ Build the HTML/CSS/JavaScript
2. ✅ Review the code for bugs
3. ✅ Open it in a browser
4. ✅ Click all buttons and test features
5. ✅ Capture screenshots
6. ✅ Analyze UI with LLaVA vision AI
7. ✅ Fix any issues found
8. ✅ Re-test until perfect

**All automatically!** No manual testing needed.

---

## 🛠️ Available MCP Tools

### Code Review
- `review_code` - Analyze files for security issues, bugs, code smells

### Browser Automation
- `browser_navigate` - Open websites/files in browser
- `browser_click` - Click elements by CSS selector
- `browser_fill` - Fill input fields
- `browser_screenshot` - Capture page screenshots
- `browser_get_errors` - Get console errors/warnings
- `browser_execute_js` - Run JavaScript in browser context
- `browser_close` - Close browser

### Visual AI Analysis
- `analyze_screenshot` - AI-powered visual analysis with LLaVA
- `detect_ui_issues` - Automated UI/UX problem detection

---

## ⚙️ Configuration

### Customize Testing Behavior

Edit `~/.rovodev/mcp_testing_server/config.json`:

```json
{
  "browser": {
    "headless": false,        // Show browser (true = hidden)
    "timeout": 30000,         // Page load timeout (ms)
    "viewport": {
      "width": 1920,
      "height": 1080
    }
  },
  "screenshots": {
    "path": "./screenshots",
    "format": "png"
  }
}
```

### Disable Auto-Testing

Remove the "AUTO-TESTING PROTOCOL" section from `~/.rovodev/config.yml`

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   RovoDev CLI (Your Interface) │
└──────────────┬──────────────────┘
               │
               ↓
┌──────────────────────────────────────────┐
│         MCP Testing Server               │
│  • Code Reviewer (static analysis)       │
│  • Browser Tester (Patchright)           │
│  • Image Analyzer (LLaVA integration)    │
└──────────┬───────────────────┬───────────┘
           │                   │
           ↓                   ↓
   ┌───────────────┐   ┌─────────────────┐
   │  Browser      │   │  Ollama+LLaVA   │
   │  Automation   │   │  Vision AI      │
   └───────────────┘   └─────────────────┘
```

---

## 📊 Comparison

| Feature | RovoDev (Before) | RovoDev + MCP Testing |
|---------|------------------|----------------------|
| Code Generation | ✅ | ✅ |
| Automated Testing | ❌ | ✅ |
| Browser Automation | ❌ | ✅ |
| Visual AI Analysis | ❌ | ✅ |
| Bug Detection | Manual | Automatic |
| Cost | - | $0 |
| Privacy | Cloud | 100% Local |

---

## 🧪 Examples

### Test a Contact Form

```
> "Build a contact form with name, email, and message fields. 
   Test it automatically with the MCP tools."
```

### Build and Test a Calculator

```
> "Create a calculator app and verify all operations work correctly."
```

### Full E2E Testing

```
> "Build a todo list with add/delete/complete features. 
   Test everything, take screenshots, and analyze the UI."
```

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- [Atlassian RovoDev CLI](https://developer.atlassian.com/cloud/acli/)
- [Ollama](https://ollama.com) - Local LLM runtime
- [LLaVA](https://llava-vl.github.io/) - Vision-language model
- [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) - Undetectable browser automation
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/rovodev-mcp-testing/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/rovodev-mcp-testing/discussions)

---

## ⭐ Star History

If this project helps you, please star it! ⭐

---

**Built with 🔥 by developers, for developers**
