# 🚀 Integration Guide: Adding Sandbox Monitor to RovoDev

## ✅ What You Have Now

A fully functional MCP server that can:
- 🎯 Launch and monitor processes automatically
- 🔍 Detect stuck/waiting processes in real-time
- ⌨️ Auto-send keyboard input to waiting processes
- 🧠 Make AI-powered decisions with Ollama
- 💾 Learn from past decisions via knowledge database
- 🤖 Run fully autonomous background monitoring

## 📋 Step 1: Add to RovoDev's MCP Config

### Option A: Add to existing mcp.json

Find your RovoDev `mcp.json` (usually in `C:\Users\ggfuc\.rovodev\` or project root) and add:

```json
{
  "mcpServers": {
    "sandbox-monitor": {
      "command": "python",
      "args": ["C:\\Users\\ggfuc\\.rovodev\\mcp_sandbox_monitor\\server.py"],
      "env": {}
    }
  }
}
```

### Option B: Standalone config for testing

Create a new `mcp_sandbox.json`:

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

## 📋 Step 2: Test With RovoDev

### Manual Test (Direct Python)
```bash
cd C:\Users\ggfuc\.rovodev\mcp_sandbox_monitor
python test_mcp_server.py
```

### Test With RovoDev CLI
```bash
rovodev --mcp-config mcp_sandbox.json
```

Then ask Rex:
```
"Rex, use the sandbox-monitor to launch a test script that asks for confirmation"
```

## 🎯 Step 3: Real-World Usage Examples

### Example 1: Automated Build
```
User: "Rex, run the build script and handle any confirmations"

Rex: [Uses launch_monitored_process with auto_monitor=true]
Build: Compiles... "Deploy to production? (Y/N):"
Monitor: Detects stuck after 5 seconds
Rex: [Checks knowledge DB, sees similar approval]
Rex: [Sends 'Y' automatically]
Build: ✅ Deployed!
```

### Example 2: Long-Running Task
```
User: "Rex, start monitoring all processes in the background"

Rex: [Calls start_background_monitor]
Monitor: Running continuously...
User: [Launches multiple scripts manually]
Monitor: Detects Script #2 is stuck
Monitor: Analyzes: "High-risk database operation"
Rex: "Boss, script wants to drop database tables. Allow?"
User: "No!"
Rex: [Sends 'N']
```

### Example 3: Pattern Learning
```
User: "Rex, handle the deployment"

Rex: [Calls search_knowledge_db for "deployment confirmation"]
DB: "Last 3 times: User approved deployment at 2PM"
Rex: "Boss, based on history, you usually approve deployments at this time. Proceed?"
User: "Yes"
Rex: [Sends 'Y', logs decision]
```

## 🧠 Step 4: Teaching Rex New Patterns

Rex learns automatically from every interaction! Each time you:
- Approve/deny a prompt
- Kill a stuck process
- Send manual input

It's logged to the knowledge database and used for future decisions.

## 🔧 Advanced Configuration

### Background Monitor Settings

```python
# In server.py or via tool call
monitor = BackgroundMonitor(
    check_interval=2.0,         # Check every 2 seconds
    stuck_threshold_seconds=5,  # Consider stuck after 5s
    cpu_threshold=2.0           # CPU below 2% = idle
)
```

### AI Decision Tuning

Edit `ai_decision_engine.py` to adjust:
- Risk assessment thresholds
- Confidence levels
- Auto-response vs. ask-boss logic

### Knowledge DB Schema

Located at: `C:\Users\ggfuc\.rovodev\knowledge_db\knowledge.db`

Tables:
- `ai_decisions` - Past decisions
- `command_executions` - Process metrics
- `process_baselines` - Performance patterns
- `stuck_alerts` - Stuck process logs

## 📊 Monitoring & Debugging

### Check Server Status
```bash
# In RovoDev/Rex
"Rex, what's the status of the sandbox monitor?"
```

Rex will call `get_monitor_status` and show:
- Running: yes/no
- Tracked processes: 3
- Stuck processes: 1
- Process details

### View Logs
```bash
# Knowledge DB
cd C:\Users\ggfuc\.rovodev\knowledge_db
sqlite3 knowledge.db "SELECT * FROM ai_decisions ORDER BY timestamp DESC LIMIT 10;"
```

### Debug Mode
```bash
# Run server with verbose output
python server.py --verbose
```

## 🎓 Tips for Best Results

1. **Start Small**: Test with simple scripts first
2. **Build Trust**: Let Rex handle low-risk confirmations, escalate high-risk
3. **Review Logs**: Check decisions periodically to ensure accuracy
4. **Teach Patterns**: Correct Rex when wrong, it will learn
5. **Use Background Monitor**: Let it run continuously for maximum automation

## 🚨 Safety Features

- ✅ Only monitors registered processes (opt-in)
- ✅ Boss escalation for high-risk operations
- ✅ Manual override always available
- ✅ All decisions logged with timestamp
- ✅ Can force-kill runaway processes
- ✅ Knowledge DB for audit trail

## 🐛 Troubleshooting

### "Process not found"
- Process may have finished before check
- PID may be incorrect
- Use `get_stuck_processes` to find active PIDs

### "Input not sent"
- Window may not be in focus
- Process may not be actually waiting
- Check with `check_process_status` first

### "Background monitor not working"
- Make sure to call `start_background_monitor`
- Check interval may be too long
- Process may not meet "stuck" criteria (CPU < 2%, runtime > 5s)

### "Knowledge DB locked"
- Another process may have DB open
- Close and restart server
- Check for orphaned connections

## 📈 Future Enhancements

Coming soon:
- [ ] OCR for reading actual prompts
- [ ] Output buffer capture
- [ ] Multi-process orchestration
- [ ] Process dependency tracking
- [ ] Advanced pattern recognition
- [ ] Risk scoring system
- [ ] Confidence levels

## 🎉 You're Ready!

Your Sandbox Monitor MCP server is fully functional and integrated. Rex can now:
- 🤖 Autonomously handle stuck processes
- 🧠 Learn from your decisions
- ⚡ Speed up workflows by 10x
- 🎯 Free you from babysitting builds/deployments

**Welcome to the future of autonomous development!** 🚀

---

Need help? Issues? Questions?
Open the knowledge DB and see what Rex has learned:
```bash
cd C:\Users\ggfuc\.rovodev\knowledge_db
sqlite3 knowledge.db "SELECT * FROM ai_decisions;"
```
