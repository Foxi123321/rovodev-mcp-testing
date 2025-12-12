# 🔥 RovoDev MCP Testing Package

**Complete MCP server suite for RovoDev: Knowledge DB, Browser Automation, Vision AI, Sandbox Monitoring, and Deep Learning Intelligence**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Required-green.svg)](https://ollama.com)
[![Release](https://img.shields.io/github/v/release/Foxi123321/rovodev-mcp-testing)](https://github.com/Foxi123321/rovodev-mcp-testing/releases)

> 6 powerful MCP servers that supercharge RovoDev with autonomous testing, knowledge management, browser automation, and AI-powered analysis.

---

## 🎯 What This Does

Six production-ready MCP servers that extend RovoDev:

### 🧠 mcp_knowledge_db
- **Code Intelligence** - Store and query code patterns, functions, classes
- **Command Baselines** - Track execution patterns and performance
- **Error Solutions** - Learn from past errors and suggest fixes
- **AI Curator** - Gemma AI manages and optimizes the knowledge base

### 🤖 mcp_sandbox_monitor
- **Process Monitoring** - Track running processes and detect stuck states
- **Auto-Response** - Automatically answer prompts in interactive scripts
- **AI Decision Engine** - Learn from past decisions
- **Background Daemon** - Autonomous monitoring without user intervention

### 🌐 mcp_unstoppable_browser
- **Cloudflare Bypass** - FlareSolverr integration for protected sites
- **Session Management** - Persistent browser sessions with cookies
- **Data Extraction** - CSS selector-based scraping
- **JavaScript Execution** - Run custom scripts in browser context

### 👁️ mcp_vision_simple
- **Screenshot Analysis** - LLaVA vision AI analyzes images
- **Async Processing** - Non-blocking image analysis
- **UI/UX Detection** - Automated visual problem detection

### 🔍 mcp_testing_server
- **Code Review** - Static analysis for security and bugs
- **Browser Testing** - Automated UI testing with Patchright
- **Visual Analysis** - AI-powered screenshot review
- **Desktop Automation** - Test desktop applications

### 🧪 mcp_deep_learning_v2
- **Code Indexing** - Advanced semantic code search with Qwen
- **Pattern Recognition** - ML-powered code understanding
- **Consensus Engine** - Multi-model verification
- **Vector Store** - Fast similarity search
- **Note**: Requires `qwen2.5-coder:7b` or `qwen3-coder:30b` (configurable)

**💯 Local & Free** - No API costs, unlimited usage, 100% private

---

## 🚀 Quick Start

### Prerequisites

- [Atlassian RovoDev CLI](https://developer.atlassian.com/cloud/acli/guides/install-acli/) installed
- [Ollama](https://ollama.com) installed
- Python 3.8+ with pip

### System Requirements

**Minimum (for basic features)**:
- 8GB RAM
- 10GB disk space
- CPU: 4+ cores recommended

**Recommended (for all AI models)**:
- 16GB RAM (for qwen3-coder:30b)
- 20GB disk space (AI models are large)
- CPU: 8+ cores for better performance
- GPU: Optional but speeds up Ollama significantly

### Installation (Windows)

**Option 1: Download Package (Recommended)**

1. Download [Latest Release](https://github.com/Foxi123321/rovodev-mcp-testing/releases/latest)
2. Extract to `C:\Users\YOUR_USERNAME\.rovodev\`
3. Open PowerShell in the folder
4. Install: `pip install -r mcp_knowledge_db/requirements.txt`
5. Pull AI models: 
   - `ollama pull gemma2:9b` (Knowledge DB AI curator)
   - `ollama pull llava:7b` (Vision analysis)
   - `ollama pull qwen2.5-coder:7b` (Deep learning code analysis - lightweight)
   - *Optional*: `ollama pull qwen3-coder:30b` (more powerful but requires 16GB+ RAM)
6. Configure in RovoDev's `mcp.json` (see examples in each server folder)
7. **Optional**: Update `mcp_deep_learning_v2/config.py` to use different Qwen models
8. Start RovoDev: `acli rovodev run`

**Option 2: Clone from GitHub**

```bash
# Clone the repository
git clone https://github.com/Foxi123321/rovodev-mcp-testing.git
cd rovodev-mcp-testing

# Install all dependencies
pip install -r mcp_knowledge_db/requirements.txt
pip install -r mcp_sandbox_monitor/requirements.txt
pip install -r mcp_unstoppable_browser/requirements.txt
pip install -r mcp_vision_simple/requirements.txt
pip install -r mcp_testing_server/requirements.txt
pip install -r mcp_deep_learning_v2/requirements.txt

# Pull required Ollama models
ollama pull gemma2:9b          # For mcp_knowledge_db
ollama pull llava:7b            # For mcp_vision_simple
ollama pull qwen2.5-coder:7b    # For mcp_deep_learning_v2 (lightweight)

# Optional: More powerful model (requires 16GB+ RAM)
# ollama pull qwen3-coder:30b

# Configure MCP servers in RovoDev
# Add server configs to ~/.rovodev/mcp.json

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

## 📋 Changelog

### v1.0.1 (Latest) - 2024-12-15
- 🐛 **Fixed**: MCP servers stdout pollution causing JSON-RPC parsing errors
- 🔧 **Fixed**: Removed print statements and StreamHandler logging from servers
- ✅ **Improved**: All servers now output clean JSON-RPC messages only
- 📝 **Changed**: Logs now go to dedicated log files instead of stdout
- 📝 **Updated**: Added qwen2.5-coder requirement and system requirements documentation

### v1.0.0 - 2024-12-14
- 🚀 Initial release with 6 MCP servers
- 🧠 Knowledge Database with AI curator
- 🤖 Sandbox Monitor with auto-response
- 🌐 Unstoppable Browser with Cloudflare bypass
- 👁️ Vision AI with LLaVA integration
- 🔍 Testing Server with browser automation
- 🧪 Deep Learning Intelligence engine

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
