# Failure-Classifier MCP Server

**Intelligent failure classification and recovery strategy - Zero guesswork**

---

## 🎯 What This Does

This MCP server analyzes failures and determines the RIGHT recovery strategy. No more blindly retrying or giving up - it makes intelligent decisions.

### Key Features
- ✅ Classifies failures into 3 categories
- ✅ Suggests specific recovery actions
- ✅ Determines if retry makes sense
- ✅ Identifies root cause (not symptoms)
- ✅ 100% local using Ollama (Gemma/Qwen)
- ✅ Zero cloud API costs

---

## 📊 Failure Categories

### 1️⃣ EXECUTION_ERROR
**What:** Implementation bug, transient error, wrong approach
**Recovery:** Fix and retry the same step
**Examples:**
- Test assertion failed (bug in code)
- Network timeout (transient)
- Wrong API call syntax

### 2️⃣ PLAN_GAP
**What:** Plan was incomplete, missing steps, wrong sequence
**Recovery:** Partial replan (affected steps only)
**Examples:**
- Missing prerequisite step
- Steps in wrong order
- Invalid assumptions in plan

### 3️⃣ MISSING_CAPABILITY
**What:** Tool/API/dependency doesn't exist
**Recovery:** Stop and report blocker
**Examples:**
- Required library not installed
- API endpoint doesn't exist
- Fundamental limitation

---

## 🚀 Available Tools

### `classify_failure`
Main classification tool.

**Input:**
- `failure_description` (string): What failed and how
- `audit_results` (object): From execution-auditor
- `original_plan` (string): The approved plan
- `error_logs` (string, optional): Error logs/stack traces

**Output:**
```json
{
  "classification": "EXECUTION_ERROR",
  "confidence": "HIGH",
  "reasoning": "Test failed due to incorrect assertion...",
  "recovery_strategy": "Fix JWT validation logic and retry",
  "affected_steps": ["Step 3: Run tests"]
}
```

### `suggest_recovery_action`
Get specific recovery steps.

### `should_retry`
Decide if retry makes sense.

**Output:**
```json
{
  "should_retry": true,
  "max_retries": 3,
  "current_retry_count": 1,
  "retries_remaining": 2,
  "recommendation": "..."
}
```

### `identify_root_cause`
Find underlying problem, not symptoms.

---

## 🔄 Workflow Integration

```
Execution Failed
    ↓
Execution-Auditor identifies what failed
    ↓
Failure-Classifier analyzes failure
    ↓
EXECUTION_ERROR → Fix code, retry step
PLAN_GAP → Revise plan, re-validate
MISSING_CAPABILITY → Stop, report blocker
```

---

## 🧪 Example Classifications

### Example 1: Execution Error
**Failure:** "Test test_auth failed: AssertionError: Expected 200, got 401"
**Classification:** EXECUTION_ERROR
**Reasoning:** Code bug in JWT validation
**Recovery:** Debug auth.py, fix validation logic, retry

### Example 2: Plan Gap
**Failure:** "Cannot connect to database - connection refused"
**Classification:** PLAN_GAP
**Reasoning:** Plan didn't include step to start database
**Recovery:** Add "Start database service" to plan before connection step

### Example 3: Missing Capability
**Failure:** "Module 'tensorflow' not found"
**Classification:** MISSING_CAPABILITY
**Reasoning:** TensorFlow not installed and not in requirements
**Recovery:** STOP - Cannot proceed without TensorFlow

---

## 📦 Integration with RovoDev

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "failure-classifier": {
      "command": "python",
      "args": ["C:/path/to/mcp_failure_classifier/server.py"],
      "env": {
        "CLASSIFIER_MODEL": "gemma2:9b",
        "OLLAMA_BASE_URL": "http://localhost:11434"
      }
    }
  }
}
```

---

## 🎓 Decision Rules

### Retry Decision Logic
```
Transient error (network, timeout) → YES, retry up to 3x
Deterministic bug → NO, fix first
After 3 retries → NO, stop wasting time
Random/intermittent → YES, max 2 retries
```

### Recovery Priority
```
1. EXECUTION_ERROR: Fix fast, retry immediately
2. PLAN_GAP: Replan affected steps only (preserve progress)
3. MISSING_CAPABILITY: Stop immediately (don't waste time)
```

---

## 🔒 Smart Recovery Features

This classifier prevents:
- ❌ Infinite retry loops
- ❌ Retrying deterministic bugs
- ❌ Full replans when partial replan works
- ❌ Continuing when blocked

Forces:
- ✅ Intelligent retry decisions
- ✅ Root cause analysis
- ✅ Minimal rework
- ✅ Fast failure on blockers

---

## 🤖 Philosophy

> "Not all failures are created equal."
> "Retry intelligently, not blindly."
> "Fix the root cause, not the symptoms."

This server embodies the **intelligent recovery principle** - fail fast on blockers, fix smart on bugs.
