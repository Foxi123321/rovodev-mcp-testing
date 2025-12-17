# Filesystem/Artifacts MCP Server

**Secure artifact storage and management - Evidence organization**

---

## 🎯 What This Does

This MCP server provides secure, organized storage for execution artifacts:
- Screenshots from browser tests
- Logs from command execution
- Test results and reports
- Files created during execution

### Key Features
- ✅ Secure path validation (prevents directory traversal)
- ✅ Unique artifact IDs with metadata
- ✅ SHA256 hash verification for integrity
- ✅ Artifact bundling (group related artifacts)
- ✅ Automatic cleanup of old artifacts
- ✅ Statistics and filtering

---

## 🚀 Available Tools

### `store_artifact`
Store an artifact with metadata.

**Input:**
- `artifact_type`: screenshot | log | test_result | report | file | other
- `file_path`: Path to file
- `metadata`: Tags, test name, execution ID, etc.

**Output:**
```json
{
  "status": "stored",
  "artifact_id": "uuid",
  "stored_path": "/path/to/artifact",
  "file_size": 1024
}
```

### `retrieve_artifact`
Get artifact metadata and verify it exists.

### `list_artifacts`
List artifacts with filters (type, execution_id, tags).

### `create_artifact_bundle`
Bundle multiple artifacts together (e.g., all from one test run).

### `get_artifact_stats`
Get storage statistics.

### `cleanup_old_artifacts`
Remove artifacts older than X days.

### `read_file_safe`
Safely read files (with size limits and path validation).

### `list_directory_safe`
List directory contents (only allowed paths).

---

## 🔒 Security Features

- **Path Validation:** Only access files within allowed directories
- **Hash Verification:** SHA256 hashes ensure file integrity
- **Size Limits:** Prevent reading massive files
- **Metadata Tracking:** Full audit trail of all artifacts

---

## 📦 Integration

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "filesystem-artifacts": {
      "command": "python",
      "args": ["C:/path/to/mcp_filesystem_artifacts/server.py"]
    }
  }
}
```

---

## 🧪 Example Usage

```python
# Store screenshot from test
artifact_id = store_artifact(
    artifact_type="screenshot",
    file_path="./screenshots/test_login.png",
    metadata={
        "test_name": "test_login",
        "execution_id": "exec_123",
        "tags": ["ui_test", "login"]
    }
)

# Store test results
store_artifact(
    artifact_type="test_result",
    file_path="./test_results.json",
    metadata={"execution_id": "exec_123"}
)

# Bundle all artifacts from test run
bundle_id = create_artifact_bundle(
    bundle_name="Login Test Results",
    artifact_ids=[screenshot_id, test_result_id],
    metadata={"execution_id": "exec_123"}
)
```

---

## 📊 Artifact Organization

```
artifacts/
├── screenshots/     # Browser/UI screenshots
├── logs/           # Execution logs
├── test_results/   # Test output files
├── reports/        # Analysis reports
├── files/          # General files
├── other/          # Misc artifacts
└── bundles/        # Artifact bundles
```

---

## 🤖 Philosophy

> "Evidence must be organized, secure, and verifiable."
> "Every claim needs artifacts to back it up."

This server provides the evidence backbone for the autonomous system.
