# 🖥️ SANDBOX MONITOR MCP - TECHNICAL PLAN

**Goal:** AI-powered system monitoring that detects stuck processes and learns patterns

---

## 🎯 CORE FEATURES

### 1. Process Monitoring
- Watch all PowerShell processes
- Track: PID, Name, CPU%, Memory, Duration
- Poll every 5 seconds
- Detect new processes and terminations

### 2. Pattern Recognition
- Store execution patterns in Knowledge DB
  - "gradle build: avg 3min, std dev 30sec"
  - "npm install: avg 45sec"
  - "python script: avg 2min"
- Learn normal behavior over time
- Flag anomalies (3x normal duration = probably stuck)

### 3. AI Decision Engine
- **Local AI (Qwen/Gemma)** - saves tokens
- Queries Knowledge DB for baselines
- Makes decision: "working" vs "stuck"
- Confidence score
- Reason for decision

### 4. Interactive Sessions
- Watch for prompts: "Do you want to continue? (Y/N)"
- Ask Rex (me) what to do
- I ask boss, get approval
- Send input to PowerShell stdin
- Continue execution

### 5. Knowledge DB Integration
- Store every command execution:
  - Command, duration, CPU avg, memory avg, exit code
  - Timestamp, success/failure
- Build baselines automatically
- Rex can query: "How long does X usually take?"

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│        SANDBOX MONITOR MCP SERVER               │
│                                                 │
│  ┌─────────────┐  ┌──────────────┐            │
│  │   Process   │  │  Pattern     │            │
│  │   Watcher   │→ │  Analyzer    │            │
│  └─────────────┘  └──────────────┘            │
│         ↓                ↓                      │
│  ┌─────────────┐  ┌──────────────┐            │
│  │ AI Decision │  │ Knowledge DB │            │
│  │   Engine    │← │  Interface   │            │
│  └─────────────┘  └──────────────┘            │
│         ↓                                       │
│  ┌─────────────┐                               │
│  │  Alerter &  │                               │
│  │ Controller  │                               │
│  └─────────────┘                               │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ MCP TOOLS

### 1. `start_monitoring`
- Start watching processes
- Input: None (runs continuously)
- Returns: Status, PID count

### 2. `check_if_stuck`
- Check if a specific process is stuck
- Input: PID or process name
- AI analyzes vs baseline
- Returns: stuck/working, confidence, reason

### 3. `get_process_baseline`
- Get normal execution time for a command
- Input: command name
- Queries Knowledge DB
- Returns: avg time, sample count, std dev

### 4. `log_execution`
- Manually log a command execution
- Input: command, duration, success
- Stores in Knowledge DB

### 5. `kill_stuck_process`
- Terminate a stuck process
- Input: PID
- Confirms with user first
- Returns: success/failure

### 6. `send_input_to_process`
- Send input to interactive session
- Input: PID, text
- Writes to stdin
- Returns: success

### 7. `get_monitoring_status`
- Get current monitoring state
- Returns: active processes, alerts, stats

---

## 📊 DATABASE SCHEMA (in Knowledge DB)

### command_executions
```sql
- id
- command_name
- full_command
- duration_ms
- cpu_avg_percent
- memory_avg_mb
- exit_code
- success (boolean)
- timestamp
- notes
```

### process_baselines
```sql
- id
- command_pattern (e.g., "gradle build")
- avg_duration_ms
- std_dev_ms
- min_duration_ms
- max_duration_ms
- sample_count
- last_updated
```

### stuck_alerts
```sql
- id
- pid
- process_name
- command
- alert_time
- reason
- ai_confidence
- resolved (boolean)
```

---

## 🤖 AI DECISION LOGIC

```python
def is_stuck(pid, current_duration):
    # Get process info
    process = get_process_info(pid)
    
    # Query Knowledge DB for baseline
    baseline = knowledge_db.get_baseline(process.command)
    
    if not baseline:
        return "UNKNOWN", "No baseline data"
    
    # Calculate deviation
    avg = baseline.avg_duration_ms
    std_dev = baseline.std_dev_ms
    
    if current_duration > (avg + 3 * std_dev):
        # Way over normal - likely stuck
        confidence = 0.9
        reason = f"Running {current_duration/avg:.1f}x normal time"
        
        # Ask AI for confirmation
        ai_decision = qwen_analyze(process, baseline, current_duration)
        
        return "STUCK", reason, confidence, ai_decision
    
    elif current_duration > (avg + 2 * std_dev):
        # Possibly stuck
        return "POSSIBLY_STUCK", "Taking longer than usual", 0.6
    
    else:
        return "WORKING", "Within normal range", 0.8
```

---

## 🚀 IMPLEMENTATION STEPS

### Step 1: Basic Process Monitor ✅
- PowerShell Get-Process wrapper
- Track PIDs, CPU, Memory
- Detect changes

### Step 2: Knowledge DB Integration
- Add tables to Knowledge DB
- Store execution data
- Build baselines

### Step 3: AI Decision Engine
- Call Qwen locally
- Compare vs baselines
- Generate alerts

### Step 4: MCP Server
- Create server.py
- Implement tools
- Register in mcp.json

### Step 5: Interactive Input
- Detect prompts in process output
- Send stdin to processes
- Handle approval flow

### Step 6: Testing
- Run test builds
- Verify detection works
- Train on YOUR system

---

## 🎯 SUCCESS CRITERIA

- ✅ Detects stuck gradle builds within 1 minute
- ✅ < 5% false positives
- ✅ Learns baselines after 5-10 executions
- ✅ Can send Y/N to interactive prompts
- ✅ Stores all data in Knowledge DB
- ✅ Rex can query execution history
- ✅ Works 24/7 without supervision

---

**LET'S BUILD THIS!** 🔥
