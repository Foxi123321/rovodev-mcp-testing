# Knowledge Database MCP Server
## The Heart of the MCP Ecosystem

Central intelligence storage and query system for code analysis, command execution patterns, error solutions, and system baselines.

---

## 🎯 Purpose

The Knowledge Database MCP is the **central brain** of the development intelligence ecosystem. It stores and provides fast access to:

- **Code Intelligence**: Functions, classes, purposes, dependencies
- **Command Patterns**: Execution history, duration baselines, resource usage
- **Error Solutions**: Known issues and their fixes
- **System Baselines**: Your machine's typical behavior

---

## ✨ Features

### Code Intelligence
- Store code analysis results from Deep Learning MCP
- Fast full-text search across code symbols
- Dependency tracking between components
- Cache results to avoid re-analysis

### Command Execution Intelligence
- Learn how long commands take on YOUR machine
- Track CPU, memory, disk, network usage
- Build baselines for "normal" behavior
- Detect when commands are taking longer than expected

### Error Solutions
- Store successful fixes for errors
- Full-text search for similar errors
- Track solution success rate
- Learn from what works

### System Baselines
- Record your machine's typical performance
- Compare current runs against historical data
- Adapt to your specific hardware

### 🤖 AI Database Curator (NEW!)
**Autonomous database management powered by Gemma 2 9B**

The AI curator automatically:
- ✨ **Cleans duplicates** - Finds and merges redundant entries
- 🗄️ **Archives old data** - Intelligently archives obsolete information
- 📊 **Updates confidence scores** - Recalculates reliability metrics
- 🚨 **Detects anomalies** - Finds unusual patterns (slow commands, high failure rates)
- 🏷️ **Auto-tags entries** - Categorizes code and errors automatically
- 🔗 **Discovers relationships** - Finds hidden correlations (e.g., "this error always happens with this command")
- 💡 **Generates insights** - Provides high-level analysis and recommendations

**Run manually or on schedule - your database stays clean and organized automatically!**

---

## 🔧 Installation

```bash
cd mcp_knowledge_db
pip install -r requirements.txt
```

---

## 🚀 Usage

### Add to MCP Configuration

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "knowledge-db": {
      "command": "python",
      "args": ["-m", "mcp_knowledge_db.server"],
      "cwd": "/path/to/workspace"
    }
  }
}
```

### Available Tools

#### 1. `query_code_knowledge`
Search for code symbols and their purposes.

```json
{
  "query": "authentication function",
  "limit": 10
}
```

#### 2. `query_command_patterns`
Get baseline behavior for a command.

```json
{
  "command": "gradle build"
}
```

Returns: Average duration, CPU usage, memory usage, success rate, confidence.

#### 3. `store_code_analysis`
Store code analysis results.

```json
{
  "file_path": "src/auth.py",
  "project_name": "MyApp",
  "language": "python",
  "symbols": [
    {
      "name": "authenticate_user",
      "type": "function",
      "purpose": "Validates user credentials and returns JWT token",
      "line_start": 45,
      "line_end": 67
    }
  ]
}
```

#### 4. `store_command_result`
Record command execution result.

```json
{
  "command": "npm install",
  "duration_ms": 12500,
  "success": true,
  "exit_code": 0,
  "cpu_avg": 45.2,
  "memory_peak_mb": 512
}
```

Automatically updates baselines!

#### 5. `get_error_solution`
Find solutions for an error.

```json
{
  "error_pattern": "ModuleNotFoundError: No module named 'requests'",
  "context": "Python import error",
  "limit": 5
}
```

#### 6. `store_solution`
Store a solution that worked.

```json
{
  "error_pattern": "ModuleNotFoundError: No module named 'requests'",
  "solution": "Run: pip install requests",
  "success": true,
  "context": "Python dependencies",
  "source": "manual"
}
```

#### 7. `get_system_baseline`
Get your machine's baseline metrics.

```json
{}
```

Returns: CPU, memory, disk, network baselines.

#### 8. `search_knowledge`
Search across all knowledge types.

```json
{
  "query": "docker build",
  "limit": 20
}
```

#### 9. `run_database_curator` 🤖
Run AI-powered database curation.

```json
{
  "tasks": []  // Empty = run all tasks
}
```

Tasks: duplicates, archiving, confidence, anomalies, tagging, relationships, insights

Returns: Complete curation report with AI analysis

#### 10. `get_database_health`
Get database health metrics.

```json
{}
```

Returns: Health score (0-100), entry counts, quality metrics

#### 11. `get_curator_insights`
Get AI-generated insights about your database.

```json
{}
```

Returns: AI analysis of patterns, recommendations, usage statistics

---

## 🗄️ Database Schema

**Location**: `~/.rovodev/knowledge_db/knowledge.db`

### Tables

- `code_files`: File metadata
- `code_knowledge`: Functions, classes, symbols
- `code_dependencies`: Relationships between code
- `command_patterns`: Execution history
- `command_baselines`: Expected behavior
- `system_metrics`: Machine performance
- `error_solutions`: Known fixes
- `troubleshooting_logs`: Problem resolution history
- `web_research_cache`: Cached web searches

### Full-Text Search

Uses SQLite FTS5 for blazing fast text search on:
- Code symbols and purposes
- Error patterns and solutions

---

## 🔗 Integration

### With Deep Learning MCP

```python
# Deep Learning MCP analyzes code
analysis_result = analyze_function("authenticate_user", "auth.py")

# Store in Knowledge DB
store_code_analysis({
    "file_path": "auth.py",
    "symbols": [analysis_result]
})

# Later: Query instead of re-analyzing
cached = query_code_knowledge("authenticate_user")
```

### With Sandbox Monitor MCP (Future)

```python
# Before running command
baseline = query_command_patterns("gradle build")
# Expected: 180000ms (3 min), CPU 60-80%

# Run monitored
result = run_monitored_command("gradle build")

# Store result
store_command_result({
    "command": "gradle build",
    "duration_ms": result.duration,
    "cpu_avg": result.cpu_avg,
    "success": result.success
})
# Baseline automatically updated!
```

---

## 📊 Learning Over Time

The database gets **smarter** as you use it:

1. **First run**: No baseline exists
2. **After 3 runs**: Low confidence baseline
3. **After 10 runs**: High confidence baseline
4. **Ongoing**: Continuous refinement

Baselines adapt to:
- Your machine specs
- Your typical workload
- Seasonal variations (system load)

---

## 🧪 Testing

```bash
python mcp_knowledge_db/test_server.py
```

---

## 🔮 Future Enhancements

### Phase 2: Semantic Search
- Add embedding-based similarity search
- Find similar code by meaning, not just keywords
- Powered by sentence-transformers

### Phase 3: Cross-Project Intelligence
- Learn patterns across multiple projects
- "In Project A, similar function took 2 min"
- Share knowledge between codebases

---

## 📝 Notes

- **SQLite**: Fast, local, no server needed
- **FTS5**: Built-in full-text search
- **Thread-safe**: Can be called from multiple MCP servers
- **Automatic cleanup**: Old metrics are pruned

---

## 🤝 Contributing

This is the heart of the ecosystem - handle with care!

When adding features:
1. Update schema.sql
2. Add migration if needed
3. Update models.py
4. Add database methods
5. Expose via MCP tool
6. Document in README

---

**Built with 🔥 by Rex & Boss**

*"The database that learns your machine"*
