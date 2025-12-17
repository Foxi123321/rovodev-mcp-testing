# Plan-Validator MCP Server

**Strict plan validation using local AI (Qwen/Gemma) - Zero API costs**

---

## 🎯 What This Does

This MCP server acts as a **gatekeeper** to prevent incomplete, vague, or unexecutable plans from being executed. It's the "four-eyes principle" for autonomous AI systems.

### Key Features
- ✅ Validates plans for completeness and clarity
- ✅ Checks if plans use only available MCP tools
- ✅ Verifies measurable success criteria exist
- ✅ Suggests improvements for failed plans
- ✅ 100% local using Ollama (Qwen/Gemma)
- ✅ Zero cloud API costs

---

## 🔧 Setup

### 1. Install Dependencies
```bash
cd mcp_plan_validator
pip install -r requirements.txt
```

### 2. Make Sure Ollama is Running
```bash
# Check Ollama is running
ollama list

# Should see qwen3-coder:30b or gemma2:9b
```

### 3. Test the Server
```bash
python server.py
```

---

## 🚀 Available Tools

### `validate_plan`
Perform full validation of an execution plan.

**Input:**
- `plan` (string, required): The plan to validate
- `context` (string, optional): Additional context about constraints
- `strict_mode` (boolean, default: true): Fail on any ambiguity

**Output:**
```json
{
  "status": "PASS" or "FAIL",
  "score": 85,
  "issues": ["Missing verification step", "Vague step 3"],
  "strict_mode": true
}
```

### `validate_plan_against_mcp_tools`
Check if plan only uses tools that actually exist.

**Input:**
- `plan` (string): The plan
- `available_tools` (array): List of available MCP tool names

**Output:**
```json
{
  "status": "FAIL",
  "missing_tools": ["non_existent_tool", "fake_api"],
  "message": "Plan references 2 tools that don't exist"
}
```

### `check_definition_of_done`
Verify plan has clear, measurable success criteria.

**Input:**
- `plan` (string): The plan to check

**Output:**
```json
{
  "status": "PASS",
  "has_definition_of_done": true,
  "details": "..."
}
```

### `suggest_plan_improvements`
Get specific suggestions for fixing a failed plan.

**Input:**
- `plan` (string): The failed plan
- `validation_errors` (array): List of validation errors

**Output:**
```json
{
  "suggestions": "ERROR: Missing verification\nFIX: Add test step...",
  "original_errors": [...]
}
```

---

## 📦 Integration with RovoDev

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "plan-validator": {
      "command": "python",
      "args": ["C:/path/to/mcp_plan_validator/server.py"],
      "env": {
        "VALIDATOR_MODEL": "qwen3-coder:30b",
        "OLLAMA_BASE_URL": "http://localhost:11434"
      }
    }
  }
}
```

---

## 🔄 Workflow Integration

### Phase-Based Execution
```
User Request
    ↓
Claude creates PLAN
    ↓
Plan-Validator MCP validates
    ↓
PASS → Execute plan
FAIL → Claude must fix plan and re-validate
```

### System Prompt Integration
Add to Rex's system prompt:

```
RULE: Execution is FORBIDDEN until Plan-Validator returns PASS.

WORKFLOW:
1. Create detailed plan
2. Call plan-validator:validate_plan
3. If FAIL: Fix issues and re-validate
4. If PASS: Proceed to execution
5. Never skip validation
```

---

## 🧪 Example Usage

### Good Plan (PASS)
```
PLAN:
1. Create file auth.py at ./src/auth.py
2. Write authentication function with JWT validation
3. Run unit tests: pytest tests/test_auth.py
4. Verify: All tests pass (exit code 0)

Definition of Done:
- File exists at ./src/auth.py
- All unit tests pass
- Code coverage > 80%
```

### Bad Plan (FAIL)
```
PLAN:
1. Fix the authentication
2. Make it secure
3. Test it
```
**Validation Result:** FAIL
- Step 1: "Fix authentication" is too vague - what specifically needs fixing?
- Step 2: "Make it secure" - no concrete actions specified
- Step 3: "Test it" - how? What tests? What's the pass criteria?
- Missing Definition of Done

---

## ⚙️ Configuration

### Environment Variables
- `VALIDATOR_MODEL`: Ollama model to use (default: `qwen3-coder:30b`)
- `OLLAMA_BASE_URL`: Ollama API URL (default: `http://localhost:11434`)

### Recommended Models
- **qwen3-coder:30b** - Best for code-related plans (recommended)
- **gemma2:9b** - Faster, good for simple validation
- **qwen2.5:14b** - Good balance of speed/accuracy

---

## 🎓 Validation Criteria

### Critical Issues (Auto-FAIL)
1. Vague/ambiguous steps
2. Missing concrete actions
3. No measurable success criteria
4. Assumes non-existent tools/APIs
5. Skips steps with "if needed"
6. No verification strategy

### Important Issues (FAIL in strict mode)
7. Steps could be more specific
8. Missing error handling
9. No rollback plan
10. Unclear dependencies

---

## 📊 Scoring System

- **90-100**: Excellent plan, clear and complete
- **80-89**: Good plan, minor improvements possible
- **70-79**: Acceptable (fails in strict mode)
- **0-69**: Poor plan, major issues

---

## 🔒 Anti-Laziness Features

This server prevents:
- ❌ "Handle edge cases" (too vague)
- ❌ "Optimize as needed" (not concrete)
- ❌ "Test thoroughly" (no specifics)
- ❌ "Fix any bugs" (no plan)

Forces:
- ✅ Specific, verifiable actions
- ✅ Measurable success criteria
- ✅ Concrete tool usage
- ✅ Clear verification steps

---

## 🤖 Philosophy

> "If you can't measure it, you can't achieve it."
> "Vague plans lead to vague results."
> "Validation prevents lazy execution."

This server embodies the **strict phase model** - no execution without validation.
