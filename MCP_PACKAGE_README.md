# 🔥 REX MCP ECOSYSTEM - Complete Package

**Six badass MCP servers ready to supercharge your AI development workflow!**

## 📦 What's Included

### 1. **Knowledge Database** (`mcp_knowledge_db/`)
AI-powered code knowledge system with:
- Semantic code search
- Command pattern tracking
- Error solution database
- AI curator (Gemma2)

### 2. **Unstoppable Browser** (`mcp_unstoppable_browser/`)
Hardcore web automation:
- Cloudflare bypass
- JavaScript execution
- Form automation
- Screenshot capture

### 3. **Sandbox Monitor** (`mcp_sandbox_monitor/`)
Process monitoring and control:
- Auto-detect stuck processes
- Smart intervention
- Background daemon mode

### 4. **Vision Server** (`mcp_vision_simple/`)
Image analysis with AI:
- Uses llava vision model
- Async analysis
- Screenshot understanding

### 5. **Testing Server** (`mcp_testing_server/`)
Code review automation:
- Lint checking
- Complexity analysis
- Test automation

### 6. **Deep Learning Intelligence** (`mcp_deep_learning_v2/`)
Advanced code analysis:
- Semantic code understanding
- Pattern recognition
- Cross-repo intelligence

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```batch
MCP_PACKAGE_INSTALLER.bat
```
This installs all Python packages needed (~5 minutes).

### Step 2: Install Ollama & AI Models
```batch
INSTALL_OLLAMA_MODELS.bat
```
This downloads 3 AI models (~30-60 minutes, 19 GB).

**OR manually:**
1. Install Ollama: https://ollama.com/download
2. Run these commands:
```bash
ollama pull gemma2:9b
ollama pull llava:latest
ollama pull qwen2.5:14b
```

### Step 3: Configure RovoDev
Copy the `mcp.json` file to your RovoDev config directory:
- Windows: `C:\Users\<YourName>\.rovodev\mcp.json`

### Step 4: Launch!
Start RovoDev and all MCP servers will auto-connect.

---

## 🧪 Testing (Optional)

Test all servers manually:
```batch
START_ALL_MCP_SERVERS.bat
```

Check individual servers:
```batch
cd mcp_knowledge_db
python server.py
```

---

## 📋 System Requirements

- **OS:** Windows 10/11 (or Linux/Mac with modifications)
- **Python:** 3.11 or higher
- **RAM:** 16 GB minimum (32 GB recommended for all models)
- **Disk:** 25 GB free (for AI models + dependencies)
- **GPU:** Optional but recommended for faster AI inference

---

## 🔧 Configuration

### Ollama Settings
Edit your environment or `mcp.json`:
```json
"env": {
  "OLLAMA_BASE_URL": "http://localhost:11434"
}
```

### Change AI Models
Edit `mcp_deep_learning_v2/config.py` or `mcp_knowledge_db/config.py`:
```python
PRIMARY_MODEL = "gemma2:9b"  # Change to any Ollama model
```

---

## 🎯 What Each Server Does

### Knowledge Database
```
Ask: "What does the authentication module do?"
Get: Instant answers from indexed code + AI analysis
```

### Unstoppable Browser
```
Command: "Go to spotify.com and play my playlist"
Result: Full browser automation with anti-detection
```

### Sandbox Monitor
```
Detects: Process waiting for input
Action: Auto-sends appropriate response based on AI
```

### Vision Server
```
Input: Screenshot of error message
Output: AI explains what's wrong and how to fix it
```

### Testing Server
```
Command: "Review this file for issues"
Result: Lint errors, complexity warnings, suggestions
```

### Deep Learning Intelligence
```
Query: "Find all database connection code"
Result: Semantic search across entire codebase
```

---

## 🛠️ Troubleshooting

### "Ollama not found"
Install from: https://ollama.com/download

### "Module not found" errors
Run the installer again:
```batch
MCP_PACKAGE_INSTALLER.bat
```

### Server won't start
Check if port is already in use:
```bash
netstat -ano | findstr :11434
```

### AI is slow
- Use smaller models: `ollama pull gemma2:2b`
- Get a GPU (10x faster)
- Increase RAM allocation

### Vision analysis fails
Make sure llava is installed:
```bash
ollama pull llava:latest
```

---

## 📁 Directory Structure

```
.
├── mcp_knowledge_db/          # Knowledge database server
├── mcp_unstoppable_browser/   # Browser automation server  
├── mcp_sandbox_monitor/       # Process monitor server
├── mcp_vision_simple/         # Vision AI server
├── mcp_testing_server/        # Testing automation server
├── mcp_deep_learning_v2/      # Deep learning server
├── mcp.json                   # RovoDev configuration
├── MCP_PACKAGE_INSTALLER.bat  # Main installer
├── INSTALL_OLLAMA_MODELS.bat  # AI model installer
└── MCP_PACKAGE_README.md      # This file
```

---

## 🔥 Advanced Usage

### Run specific servers only
Edit `mcp.json` and remove unwanted servers.

### Use different AI models
Available models: https://ollama.com/library

Install any model:
```bash
ollama pull <model-name>
```

Update config files to use it.

### Custom prompts
Edit the prompt templates in each server's `config.py`.

### Add more languages
Add to `SUPPORTED_EXTENSIONS` in `mcp_deep_learning_v2/config.py`.

---

## 🤝 Integration with RovoDev

All servers use the **MCP (Model Context Protocol)** standard:
- RovoDev auto-discovers servers from `mcp.json`
- Servers expose tools that RovoDev can call
- Bidirectional communication via stdio

No manual connection needed - just start RovoDev!

---

## 📝 Credits

Built by Rex for the ultimate AI development experience.

**MCP Protocol:** Anthropic  
**AI Models:** Ollama community  
**Browser Engine:** Patchright + Selenium  

---

## 🚨 Known Issues

1. **Deep Learning V2** - First analysis is slow (30s+) while models load
2. **Browser** - Some sites may detect automation despite bypass
3. **Vision** - Large images (>10MB) may timeout
4. **Sandbox** - Windows Defender may flag process monitoring

All servers tested and working as of Dec 2024.

---

## 💡 Tips

- **Speed up AI:** Use GPU-enabled Ollama
- **Save bandwidth:** Only install models you need
- **Debug issues:** Check server windows for error messages
- **Memory:** Close unused servers if RAM is tight

---

**Ready to dominate? Run the installer and let's go! 🚀**
