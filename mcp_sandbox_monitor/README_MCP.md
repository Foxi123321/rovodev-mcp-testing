# Sandbox Monitor MCP Server

**Autonomous process monitoring and auto-response system for RovoDev/Rex**

## 🎯 What It Does

This MCP server gives Rex the ability to:
- Launch processes and automatically monitor them
- Detect when processes are stuck waiting for input
- Auto-respond to interactive prompts (Y/N confirmations, etc.)
- Learn from past decisions via knowledge database
- Run fully autonomous background monitoring

## 🚀 Quick Start

### 1. Add to RovoDev's MCP Config

Add this to your `mcp.json`:

```json
{
  "mcpServers": {
    "sandbox-monitor": {
      "command": "python",
      "args": ["C:\\Users\\ggfuc\\.rovodev\\mcp_sandbox_monitor\\server.py"]
    }
  }
}
```

### 2. Test It

Run the server:
```bash
python server.py
```

Or use the batch file:
```bash
START_MCP_SERVER.bat
```

## 📋 Available Tools

### `launch_monitored_process`
Launch a process with automatic monitoring
```json
{
  "command": "Write-Host 'Test'; $x = Read-Host 'Continue?'",
  "visible": true,
  "auto_monitor": true
}
```

### `check_process_status`
Check if a process is running/stuck
```json
{
  "pid": 12345
}
```

### `send_input_to_process`
Send keyboard input to a waiting process
```json
{
  "pid": 12345,
  "input_text": "Y"
}
```

### `get_stuck_processes`
Get all currently stuck processes
```json
{}
```

### `start_background_monitor`
Start autonomous monitoring daemon
```json
{
  "check_interval": 2.0
}
```

### `stop_background_monitor`
Stop the background monitor
```json
{}
```

### `get_monitor_status`
Get current monitoring status
```json
{}
```

### `search_knowledge_db`
Search past decisions
```json
{
  "query": "deployment confirmation",
  "limit": 5
}
```

### `kill_process`
Force kill a process
```json
{
  "pid": 12345
}
```

### `analyze_process_behavior`
Get detailed behavior analysis
```json
{
  "pid": 12345
}
```

## 💡 Example Use Cases

### Automated Build Pipeline
```
Rex: Launches build with launch_monitored_process
Build: Compiles... asks "Deploy to production? (Y/N)"
Monitor: Detects stuck, analyzes question
Rex: Checks knowledge DB, sees similar approval
Rex: Sends 'Y' via send_input_to_process
Build: Deploys successfully
Monitor: Logs decision for future reference
```

### Long-Running Tasks
```
Rex: Starts background_monitor
User: Launches multiple scripts
Monitor: Watches all processes automatically
Monitor: Detects Script #2 is stuck
Monitor: Analyzes, decides to ask boss
Rex: "Boss, script wants to overwrite files. Allow?"
User: "Yes"
Rex: Sends approval, logs decision
```

## 🧠 Intelligence Features

- **Pattern Learning**: Remembers past decisions
- **Risk Assessment**: Identifies high-risk operations
- **Auto-Response**: Handles routine confirmations
- **Boss Escalation**: Asks when uncertain
- **Knowledge Base**: Builds up expertise over time

## 🔧 Architecture

```
RovoDev/Rex (MCP Client)
    ↓
server.py (MCP Server)
    ↓
background_monitor_daemon.py (Autonomous monitoring)
    ↓
├── process_monitor.py (Metrics tracking)
├── interactive_controller.py (Input sending)
├── ai_decision_engine.py (AI reasoning)
└── knowledge_db_interface.py (Learning/memory)
```

## 📊 Status Monitoring

Rex can check status anytime:
```python
status = call_tool("get_monitor_status")
# Returns: {running: true, tracked_processes: 3, stuck_processes: 1}
```

## 🎓 Learning System

Every decision is logged:
- Scenario (what happened)
- Context (process details)
- Decision (what was chosen)
- Outcome (result)

Future similar situations reference past decisions for smarter choices.

## 🚨 Safety Features

- Only monitors registered processes (opt-in)
- Boss escalation for high-risk operations
- Manual override available
- All decisions logged
- Can kill runaway processes

## 📝 TODO

- [ ] OCR for reading actual terminal prompts
- [ ] Output buffer capture
- [ ] Multi-process orchestration
- [ ] Advanced pattern recognition
- [ ] Confidence scoring
- [ ] Process dependency tracking

---

**Built for Rex - Making autonomous process management a reality** 🤖
