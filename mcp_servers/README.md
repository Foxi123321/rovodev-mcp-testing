# 🛠️ MCP-Server Übersicht

Alle 17 MCP-Server des RovoDev-Ökosystems.

## 📋 Server-Liste

| Server | Beschreibung | Hauptfunktion |
|--------|-------------|---------------|
| `mcp_api_testing` | API Testing & Schema Validation | API-Calls aufzeichnen, replays, Schema-Drift erkennen |
| `mcp_deep_learning_v2` | Dual-AI Code Analysis | Code-Analyse mit DeepSeek + Qwen |
| `mcp_deployment` | Docker/Container Management | Docker build, run, compose orchestration |
| `mcp_execution_auditor` | Execution Verification | Plan vs. Execution Verification |
| `mcp_failure_classifier` | Intelligent Failure Recovery | Fehler klassifizieren und Recovery vorschlagen |
| `mcp_filesystem_artifacts` | Secure Artifact Storage | Logs, Screenshots, Test-Results speichern |
| `mcp_gitops` | Git Operations | Git status, commit, branch, stash automation |
| `mcp_knowledge_database` | Knowledge Base & Memory | Conversation Memory, Solutions, Command History |
| `mcp_plan_validator` | Harsh Plan Validation | Pläne validieren mit Gemma2:9b |
| `mcp_planner` | AI-powered Task Planning | Tasks dekomponieren, Dependencies analysieren |
| `mcp_rex_cognitive_framework` | Cognitive Exploration | OBSERVE → DECIDE → ACT → LEARN Loop |
| `mcp_sandbox_monitor` | Safe Process Monitoring | Commands in Sandbox ausführen, Auto-Recovery |
| `mcp_testing_server` | Testing Tools | Browser Testing, Desktop Automation, Screenshots |
| `mcp_unstoppable_browser` | Advanced Browser Automation | Playwright + FlareSolverr für komplexe Sites |
| `mcp_vision_simple` | Vision AI | Llava für Screenshot-Analyse |
| `rex_cognitive_framework_workspace` | Cognitive Framework (Workspace) | Alternative Implementation |
| `rex_task_orchestrator` | Task Orchestration | Workflows, Visual Tests, Decision Engine |

## 🔄 Server-Interaktionen

```
User Request
     ↓
[mcp_knowledge_database] ← Memory-First: Check past solutions
     ↓
[mcp_planner] ← Decompose task
     ↓
[mcp_plan_validator] ← Validate plan (MUST PASS)
     ↓
[mcp_deep_learning_v2] ← Analyze code
     ↓
[mcp_gitops] ← Track changes
     ↓
[mcp_sandbox_monitor] ← Execute safely
     ↓
[mcp_execution_auditor] ← Verify execution
     ↓
[mcp_filesystem_artifacts] ← Store evidence
     ↓
[mcp_knowledge_database] ← Store learnings
```

## 🚀 Verwendung

Jeder Server kann individuell gestartet werden oder als Teil des gesamten MCP-Ökosystems verwendet werden.

Siehe individuelle README-Files in jedem Server-Ordner für Details.
