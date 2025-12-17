# GitOps MCP Server

Local git operations for development workflow automation.

## Tools

- `git_status` - Get repository status
- `git_diff` - Show changes
- `git_commit` - Create commits
- `git_branch` - Manage branches
- `git_log` - View history
- `git_add` - Stage files
- `git_reset` - Unstage/reset
- `git_stash` - Stash changes

## Usage

```json
{
  "mcpServers": {
    "gitops": {
      "command": "python",
      "args": ["path/to/mcp_gitops/server.py"]
    }
  }
}
```
