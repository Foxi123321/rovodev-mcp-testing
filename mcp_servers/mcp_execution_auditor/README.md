# Execution-Auditor MCP Server

**Verifies execution against approved plans - Evidence-based validation**

---

## 🎯 What This Does

This MCP server acts as a **post-execution verifier** that compares what was PLANNED vs what was actually DONE. It prevents declaring success without evidence.

### Key Features
- ✅ Step-by-step audit: DONE, FAILED, or BLOCKED
- ✅ Verifies Definition of Done was met
- ✅ Checks evidence quality (STRONG, WEAK, NONE)
- ✅ Detects skipped steps and scope creep
- ✅ 100% local using Ollama (Qwen)
- ✅ Zero cloud API costs

---

## 🔧 Setup

### 1. Install Dependencies
```bash
cd mcp_execution_auditor
pip install -r requirements.txt
```

### 2. Make Sure Ollama is Running
```bash
ollama list
# Should see qwen3-coder:30b
```

---

## 🚀 Available Tools

### `audit_execution`
Full audit of execution vs approved plan.

**Input:**
- `approved_plan` (string): The original validated plan
- `execution_summary` (string): What was actually done
- `artifacts` (object): Evidence (files, tests, logs, screenshots)

**Output:**
```json
{
  "overall_status": "PASS" or "FAIL",
  "completion": "8/10",
  "steps": [
    {
      "step": "Create auth.py",
      "status": "DONE",
      "evidence": "File exists at ./src/auth.py",
      "reason": "Confirmed by artifacts"
    },
    {
      "step": "Run tests",
      "status": "FAILED",
      "evidence": "Test output shows 2 failures",
      "reason": "Not all tests passed"
    }
  ],
  "statistics": {
    "total_steps": 10,
    "done": 8,
    "failed": 1,
    "blocked": 1
  }
}
```

### `verify_definition_of_done`
Check if DoD criteria were actually met.

**Input:**
- `definition_of_done` (string): DoD from the plan
- `artifacts` (object): Evidence

**Output:**
```json
{
  "overall_status": "PASS",
  "criteria_met": "4/4",
  "all_criteria_met": true,
  "criteria": [...]
}
```

### `compare_plan_vs_execution`
Simple comparison of planned vs executed steps.

### `check_evidence_quality`
Assess if evidence is sufficient for a claim.

---

## 🔄 Workflow Integration

```
Execution Complete
    ↓
Gather artifacts (tests, logs, screenshots)
    ↓
Execution-Auditor MCP audits
    ↓
✅ ALL DONE → Success
❌ ANY FAILED/BLOCKED → Failure Recovery
```

---

## 🧪 Example Audit

### Scenario: Authentication Implementation

**Approved Plan:**
```
1. Create auth.py with JWT validation
2. Add error handling for expired tokens
3. Run pytest tests/test_auth.py
4. Verify all tests pass (exit code 0)

DoD:
- File exists at ./src/auth.py
- All tests pass
- Coverage > 80%
```

**Execution Summary:**
```
Created auth.py with JWT function
Added TokenExpiredError handling
Ran tests - 3 passed, 1 failed
```

**Artifacts:**
```json
{
  "files_created": ["./src/auth.py"],
  "tests_run": [
    {"name": "test_valid_token", "status": "pass"},
    {"name": "test_expired_token", "status": "pass"},
    {"name": "test_invalid_signature", "status": "pass"},
    {"name": "test_malformed_token", "status": "fail"}
  ],
  "logs": "pytest exit code: 1"
}
```

**Audit Result:**
```json
{
  "overall_status": "FAIL",
  "completion": "3/4",
  "steps": [
    {"step": "Create auth.py", "status": "DONE"},
    {"step": "Add error handling", "status": "DONE"},
    {"step": "Run tests", "status": "DONE"},
    {"step": "All tests pass", "status": "FAILED"}
  ]
}
```

**Verdict:** FAIL - Not all tests passed. Must fix failing test before completion.

---

## 📦 Integration with RovoDev

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "execution-auditor": {
      "command": "python",
      "args": ["C:/path/to/mcp_execution_auditor/server.py"],
      "env": {
        "AUDITOR_MODEL": "qwen3-coder:30b",
        "OLLAMA_BASE_URL": "http://localhost:11434"
      }
    }
  }
}
```

---

## 🎓 Status Definitions

### DONE ✅
- Clear evidence the step was completed as planned
- Artifacts prove success
- All acceptance criteria met

### FAILED ❌
- Step was attempted but did not succeed
- Evidence shows errors or failures
- Does not meet acceptance criteria

### BLOCKED 🚫
- Step was not attempted
- Missing from execution summary
- No evidence provided

---

## 🔒 Anti-Cheating Features

This auditor prevents:
- ❌ Claiming success without evidence
- ❌ Declaring "done" when tests failed
- ❌ Skipping steps and hoping nobody notices
- ❌ Vague execution summaries

Forces:
- ✅ Evidence for every claim
- ✅ Honest status reporting
- ✅ Complete execution
- ✅ Measurable verification

---

## 🤖 Philosophy

> "Without evidence, it didn't happen."
> "Saying it's done doesn't make it done."
> "The auditor is not your friend."

This server embodies the **verification principle** - trust but verify, always.
