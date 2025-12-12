# Sandbox Monitor Features Checklist

## ✅ IMPLEMENTED

### Core Monitoring
- [x] Launch processes in visible windows
- [x] Track process PID correctly
- [x] Monitor CPU, memory, runtime
- [x] Detect stuck/waiting processes
- [x] Send keyboard input to processes

### Intelligence
- [x] AI decision engine (Ollama integration)
- [x] Knowledge database for decisions
- [x] Background autonomous monitoring
- [x] Pattern detection (low CPU = stuck)

### Database
- [x] Store execution records
- [x] Store AI decisions
- [x] Search past decisions
- [x] Process baselines & statistics

## ⏳ PLANNED (For MCP Server)

### Advanced Analysis
- [ ] OCR/screen reading to detect actual prompts
- [ ] Parse terminal output to identify questions
- [ ] Sentiment analysis of error messages
- [ ] Process behavior pattern learning
- [ ] Anomaly detection (beyond just stuck)

### MCP Integration
- [ ] MCP server wrapper
- [ ] Tool: `launch_monitored_process`
- [ ] Tool: `check_process_status`
- [ ] Tool: `send_input_to_process`
- [ ] Tool: `get_stuck_processes`
- [ ] Tool: `analyze_process_behavior`
- [ ] Tool: `search_knowledge_db`

### Smart Features
- [ ] Auto-learn from user corrections
- [ ] Confidence scoring for decisions
- [ ] Risk assessment (high/medium/low)
- [ ] Process dependency tracking
- [ ] Multi-process orchestration

### Output Analysis
- [ ] Capture terminal output buffer
- [ ] Parse logs for errors
- [ ] Extract structured data from output
- [ ] Regex pattern matching
- [ ] Natural language understanding of prompts

## 🎯 Priority for MCP Server

1. **Create MCP server wrapper** (server.py)
2. **Define MCP tools** for Rex to call
3. **Add output capture** (read what process is actually asking)
4. **Enhance AI reasoning** (better decision making)
5. **Pattern learning** (get smarter over time)
