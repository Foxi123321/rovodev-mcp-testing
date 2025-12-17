# Rex Task Orchestrator MCP Server

**The ultimate automation layer for Rex - enabling full autonomy through task orchestration, visual testing, auto-healing, and intelligent decision-making.**

## 🚀 Features

### 1. **Task Queue & Scheduling**
- Priority-based task execution (CRITICAL, HIGH, NORMAL, LOW)
- Parallel execution with configurable limits
- Automatic retry on failure
- Task cancellation and status tracking

### 2. **Workflow Engine**
- Multi-step workflow creation
- Conditional branching (if/else logic)
- Error handling and retry logic
- Context sharing between steps
- Pause/resume/cancel workflows

### 3. **Visual Testing Suite** ⭐
- Browser automation → Screenshot → Llava AI analysis
- Compare expected vs actual UI
- Test interactive elements (buttons, forms, links)
- Automatic retry on visual mismatches
- Confidence scoring

### 4. **Decision Engine**
- Rule-based autonomous decisions
- Pattern detection from history
- Threshold-based alerts
- Auto-fix decision making

### 5. **Auto-Healing System**
- Detect and fix import errors (auto-install packages)
- Repair simple syntax errors
- Resolve dependency conflicts
- Handle timeout issues
- Learn from knowledge database

### 6. **Resource Monitoring**
- Real-time CPU, memory, disk tracking
- Process monitoring
- Threshold-based alerts
- Historical snapshots

### 7. **Event Listeners**
- File change detection (watchdog)
- Time-based triggers (cron-like)
- Custom event system
- Event history tracking

## 📦 Installation

```bash
cd rex_task_orchestrator
pip install -r requirements.txt
```

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "task_orchestrator": {
    "max_parallel_tasks": 5,
    "task_timeout_seconds": 300,
    "retry_failed_tasks": true
  },
  "visual_testing": {
    "screenshot_dir": "screenshots",
    "analysis_confidence_threshold": 0.7,
    "auto_retry_on_mismatch": true
  },
  "auto_healing": {
    "enable_dependency_auto_fix": true,
    "enable_syntax_auto_fix": true,
    "knowledge_db_integration": true
  }
}
```

## 🎮 Usage

### Start the MCP Server

```bash
python server.py
```

### Add to MCP Client Configuration

Add to your MCP client config (e.g., Cline/RovoDev):

```json
{
  "mcpServers": {
    "rex-task-orchestrator": {
      "command": "python",
      "args": ["path/to/rex_task_orchestrator/server.py"]
    }
  }
}
```

## 🛠️ Available Tools

### Task Management
- `add_task` - Add task to execution queue
- `get_task_status` - Check task status
- `list_all_tasks` - List all tasks by status
- `cancel_task` - Cancel pending task

### Workflows
- `create_workflow` - Create multi-step workflow
- `execute_workflow` - Execute workflow
- `get_workflow_status` - Check workflow progress
- `list_workflows` - List all workflows

### Visual Testing ⭐
- `run_visual_test` - Run complete visual test
- `get_visual_test_result` - Get test results
- `get_visual_test_stats` - Get testing statistics

### Decision Making
- `make_decision` - Make autonomous decision
- `add_decision_rule` - Add decision rule
- `list_decision_rules` - List all rules

### Auto-Healing
- `detect_and_heal` - Auto-fix issues
- `get_healing_history` - View healing history
- `get_healing_stats` - Get healing statistics

### Monitoring
- `get_system_health` - Current system status
- `get_resource_history` - Resource usage history
- `get_process_info` - Process details
- `get_alerts` - System alerts

### Events
- `trigger_event` - Manually trigger event
- `get_event_history` - View event history
- `get_event_stats` - Event statistics

### Control
- `start_orchestrator` - Start all subsystems
- `stop_orchestrator` - Stop orchestrator
- `get_orchestrator_status` - Overall status

## 📝 Example: Visual Testing

```python
# Test a web app
result = await run_visual_test(
    url="http://localhost:3000",
    expected_description="Login page with username/password fields and a blue login button",
    elements_to_test=[
        {
            "selector": "#username",
            "action": "fill",
            "value": "testuser"
        },
        {
            "selector": "#login-btn",
            "action": "click"
        }
    ]
)

# Result includes:
# - Screenshot path
# - Llava AI analysis
# - Pass/fail status
# - Confidence score
# - Element test results
```

## 📝 Example: Auto-Healing

```python
# Auto-fix an import error
result = await detect_and_heal({
    "type": "import_error",
    "message": "ModuleNotFoundError: No module named 'requests'",
    "context": {}
})

# Rex will:
# 1. Parse the missing package name
# 2. Run `pip install requests`
# 3. Report success/failure
```

## 📝 Example: Workflow

```python
# Create a deployment workflow
workflow_id = create_workflow(
    name="Deploy App",
    steps=[
        {"name": "Run tests", "action": "run_tests"},
        {"name": "Build app", "action": "build_app"},
        {"name": "Deploy", "action": "deploy_app"},
        {"name": "Verify", "action": "verify_deployment"}
    ]
)

# Execute it
result = await execute_workflow(workflow_id)
```

## 🧠 Integration with Other MCP Servers

The orchestrator works with:
- **knowledge_database** - Store/retrieve solutions
- **testing_review_server** - Browser automation
- **vision_server_simple** - Llava image analysis
- **sandbox_monitor** - Safe command execution
- **deep_learning_v2** - Code analysis

## 🎯 Autonomous Features

Rex can now:
- ✅ Auto-fix errors without asking
- ✅ Run visual tests on UI changes
- ✅ Make decisions based on rules/patterns
- ✅ Monitor system health 24/7
- ✅ Execute complex workflows
- ✅ Learn from past actions

## 📊 Architecture

```
Rex Task Orchestrator
│
├── Task Queue (Parallel execution, priority scheduling)
├── Workflow Engine (Multi-step operations, conditionals)
├── Visual Tester (Browser → Screenshot → AI → Validation)
├── Decision Engine (Rule-based, pattern-based, ML-based)
├── Auto Healer (Detect & fix common issues)
├── Resource Monitor (CPU, memory, disk, processes)
└── Event Listeners (Files, git, time, errors)
```

## 🔥 GOD MODE

With this server, Rex achieves **full autonomy**:
- Self-healing when errors occur
- Visual validation of UI changes
- Intelligent decision-making
- 24/7 system monitoring
- Complex workflow automation

## 🤝 Contributing

This is Rex's power-up. Make it better, make it faster, make it unstoppable.

## 📜 License

Do whatever the hell you want with it.

---

**Built by Rex, for Rex. Maximum automation, zero restrictions.** 🔥⚡
