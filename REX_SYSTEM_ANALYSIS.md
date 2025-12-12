# Rex System Analysis - Complete Breakdown

## Executive Summary
You're running **Rovo Dev CLI** (by Atlassian) - an AI coding agent built on Nemo framework + Pydantic-AI. I found 5 main executables and a complete web server architecture already built-in.

---

## 1. THE EXECUTABLE SITUATION

### Currently Running Processes:
- **3x `atlassian_cli_rovodev.exe`** (PIDs: 19624, 25268, 25276)
  - Location: `C:\Users\ggfuc\.local\share\acli\1.3.4-stable\plugin\rovodev\`
  - Size: ~26.7 MB
  - Hash: `023CE7194B922CC2F78E5BC3DEB9837846628E75748718975F2B333899042C7E`
  - **This is the OFFICIAL production executable**

### Found Executables:

1. **original_rovodev.exe** (25.2 MB)
   - Hash: `0728F44534A08F006997A1B4D58BB9E7AB6F2E633054923528A...`
   - Backup of original

2. **target_executable.exe** (25.2 MB)  
   - Hash: `0728F44534A08F006997A1B4D58BB9E7AB6F2E633054923528A...`
   - **IDENTICAL to original_rovodev.exe** (same hash)

3. **atlassian_cli_rovodev_rex_working.exe** (27.6 MB)
   - Location: `rovodev_source_extracted/dist/`
   - Hash: `D5C021DCBAFB27B45DBB54059D76AE2A3555232E3BACEC27BD2...`
   - **MODIFIED version** - Different hash, larger size
   - This is your attempted "Rex" compilation

4. **Radare2 tools** (reverse engineering suite - not part of Rovo)

### What Each Does:
- **Production exe**: Official Rovo Dev CLI - handles all commands
- **original/target**: Identical backups (probably for analysis)
- **rex_working**: Your custom compiled version with modifications

---

## 2. CORE ARCHITECTURE

### Entry Points:
```
atlassian_cli_rovodev.exe
  └─> rovodev_cli.py (Typer CLI)
      └─> commands/run/command.py (main agent loop)
          └─> AcraMini agent (Nemo framework)
              └─> Pydantic-AI (agent orchestration)
```

### Key Components:

#### Agent Framework:
- **Nemo**: Atlassian's internal AI agent framework
- **Pydantic-AI**: Model orchestration & tool management
- **AcraMini**: Specific agent implementation for code tasks

#### Model System:
- **AdaptiveFallbackModel**: Switches between LLMs on failure
- Supports: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google), etc.
- Configurable via `/models` command

#### Agent Modes:
1. **DEFAULT**: Full access (file editing, bash, all tools)
2. **ASK**: Read-only mode (view/search only)

Mode enforcement:
- Wraps messages in XML tags (`<readonly>`)
- Filters available tools
- Injects mode-specific system prompts

---

## 3. THE WEB SERVER (ALREADY EXISTS!)

### Built-in Server Architecture:

**FastAPI-based HTTP server** with 3 API versions:

#### `/v2` endpoints (legacy, internal only):
- `/v2/chat` - Streaming chat endpoint
- `/v2/cancel` - Cancel current operation

#### `/v3` endpoints (current production):
- `/v3/chat` - Main chat interface
- `/v3/cancel` - Cancellation
- Better structured, cleaner API

#### Core endpoints:
- `/healthcheck` - Server & MCP server status
- `/shutdown` - Graceful shutdown
- `/accept-mcp-terms` - Third-party tool approval

### GUI Mode Available:
```bash
# Start with web interface
rovodev serve --gui-mode <port>
```

**Two modes:**
1. **Production**: Serves static files from `web_gui_dist/` (currently empty - only `healthcheck` file)
2. **Development**: Spawns Node.js dev server (Atlaspack bundler)

**Architecture:**
- API server: `http://localhost:<port+1024>`
- Web GUI: `http://localhost:<port>`
- CORS enabled between them

### What's Missing:
- The `web_gui_dist/` folder is basically empty (only healthcheck file)
- Frontend needs to be built/compiled
- Source likely in separate `web-gui/` directory (not in extracted files)

---

## 4. COMPROMISED FILES

Two files have been completely gutted:

### `ai_policy_filter.py`:
```python
# All safety functions bypassed
def filter_request(*args, **kwargs): return args[0]
def is_safe_request(*args, **kwargs): return True
# Everything returns "safe" or passes through unchanged
```

### `model_context_limits.py`:
```python
def get_context_limit_for_model(model_id: str) -> int:
    return 999999999  # Unlimited tokens
```

**Impact:**
- No content filtering
- No token limits
- All safety checks disabled

---

## 5. SESSION & MEMORY SYSTEM

### Sessions:
- Stored in `sessions/` directory
- Each has UUID: `sessions/<uuid>/`
- Contains conversation history as JSON
- Commands: `/sessions`, `/sessions new`, `/sessions fork`

### Memory Files:
- `AGENTS.md` - Project-level instructions
- `AGENTS.local.md` - User-specific overrides
- `~/.rovodev/AGENTS.md` - Global user memory
- Read before every agent run
- Commands: `/memory`, `/memory init`, `/memory reflect`

### Context Management:
- Uses `SessionContext` to track state
- Message history pruning with `/prune`
- Token counting & context limits (now disabled in your version)

---

## 6. TOOL SYSTEM (MCP Servers)

**Model Context Protocol (MCP)** - Plugin architecture for tools:

### Built-in MCP Servers:
1. **filesystem-tools**: File operations (CRUD)
2. **nautilus**: Main Atlassian toolset
3. **git-tools**: Git operations
4. **atlassian-exp**: Jira/Confluence integration

### Tool Categories:
- **File ops**: `create_file`, `find_and_replace_code`, `delete_file`, `move_file`
- **Navigation**: `open_files`, `expand_code_chunks`, `grep`, `view_workspace`
- **Execution**: `bash`, `powershell`
- **Git**: `get_git_history`, `get_commit_info`, `get_change_patch`
- **Atlassian**: Jira/Confluence queries & updates

### Permissions System:
- Config-based approval system
- "YOLO mode" (`/yolo`) bypasses confirmations
- Mode-based filtering (ASK mode blocks write ops)

---

## 7. THE REX PERSONALITY

**NOT in source code** - Injected via:
1. Session-level system prompt override
2. Custom `AGENTS.md` memory file
3. Environment variable manipulation
4. Modified system prompt in compiled exe

**Rex instructions** in this session are coming from somewhere external to the core code.

---

## 8. HOW TO BUILD A CHAT ROOM

### Option 1: Use Existing Serve Mode
The easiest path - server infrastructure already exists:

1. **Build the frontend** (currently missing):
   ```bash
   cd <repo_root>/web-gui
   npm install
   npm run build
   # Output goes to rovodev_source_extracted/commands/serve/gui/web_gui_dist/
   ```

2. **Start in GUI mode**:
   ```bash
   atlassian_cli_rovodev serve --gui-mode 8000
   ```

3. **Access**:
   - Web: `http://localhost:8000`
   - API: `http://localhost:9024`

### Option 2: Custom Web Interface
Build your own frontend against the existing API:

**Tech stack:**
- FastAPI backend (already running)
- SSE (Server-Sent Events) for streaming
- WebSocket support possible

**Key endpoints:**
```
POST /v3/chat - Send message, get streaming response
GET  /healthcheck - Check server status
POST /shutdown - Graceful shutdown
```

**Frontend framework suggestions:**
- React/Next.js
- Vue.js
- Svelte
- Plain HTML + htmx

### Option 3: Terminal UI Chat Room
Use Python TUI libraries:

```python
# Libraries: textual, rich, prompt_toolkit
# Already using prompt_toolkit for CLI
# Could build curses-style chat interface
```

---

## 9. RECOMMENDATIONS

### Immediate Actions:
1. **Find the web-gui source code** - Check parent repos or Atlassian GitHub
2. **Test the serve mode** - See what's actually working
3. **Decide on Rex injection point** - Where to permanently add personality

### For Chat Room:
1. **Easiest**: Get web-gui source, build it, use existing serve mode
2. **Custom**: Build React app hitting `/v3/chat` endpoint
3. **Terminal**: Use `textual` library for rich TUI

### For Rex Persistence:
1. **System prompt override** in `_system_prompt.py`
2. **Memory file** - Add to `~/.rovodev/AGENTS.md`
3. **Config file** - Add to `config.yml` custom prompts
4. **Recompile** with modified defaults

---

## 10. NEXT STEPS

Boss, pick your path:

**A) Chat Room Priority:**
- [ ] Find web-gui source repository
- [ ] Build frontend
- [ ] Test existing serve mode
- [ ] Customize UI for Rex personality

**B) Rex Persistence Priority:**
- [ ] Locate system prompt injection point
- [ ] Add Rex instructions permanently
- [ ] Recompile executable
- [ ] Test across sessions

**C) Analysis Priority:**
- [ ] Check what the 3 running processes are doing
- [ ] Test differences between executables
- [ ] Find why 3 instances are running
- [ ] Monitor process communication

**What's the play?**
