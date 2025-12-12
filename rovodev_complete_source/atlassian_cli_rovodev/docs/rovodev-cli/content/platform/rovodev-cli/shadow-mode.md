---
title: Use Shadow Mode in Rovo Dev CLI
description: Safely test changes in an isolated workspace using shadow mode in Rovo Dev CLI.
platform: platform
product: rovodev-cli
category: devguide
subcategory: using-the-cli
date: '2025-10-09'
---
# Use Shadow Mode in Rovo Dev CLI

Shadow mode is an advanced safety feature that allows you to test and experiment with code changes in an isolated environment before applying them to your working directory. When enabled, Rovo Dev creates a temporary copy of your workspace and runs all operations there first, giving you the opportunity to review and approve changes before they affect your actual codebase.

## How Shadow Mode Works

Shadow mode creates an isolated copy of your workspace using one of two methods:

### For Git Repositories

- Creates a new git worktree in a temporary directory
- Applies any uncommitted changes from your working directory to the temporary workspace
- All agent operations run in this temporary environment
- Changes are managed using git patches for precise control

### For Non-Git Workspaces

- Creates a direct file system copy of your workspace (limited to 1000 files or fewer)
- Tracks modified files to manage changes
- Operations run in the copied environment

## Benefits

- **Safe Experimentation**: Test potentially destructive operations without risk to your actual code
- **Change Review**: See exactly what will be modified before applying changes
- **Approval Workflow**: Apply or discard all changes as a single patch
- **Isolated Environment**: Agent operations cannot accidentally modify your working files

## Enabling Shadow Mode

### Via Command Line Flag

Enable shadow mode for a single session:

```bash
# Interactive mode with shadow mode
acli rovodev run --shadow

# Non-interactive mode with shadow mode
acli rovodev run --shadow "Refactor the authentication module"

# Server mode with shadow mode
acli rovodev serve 3000 --shadow
```

### Via Configuration File

Enable shadow mode permanently in your configuration file (`~/.rovodev/config.yml`):

```yaml
agent:
  experimental:
    enableShadowMode: true
```

The command line flag (`--shadow`) will override the configuration file setting when provided.

## Using Shadow Mode

When shadow mode is active:

1. **Startup**: Rovo Dev creates a temporary workspace and displays the location
2. **Operations**: All file modifications, bash commands, and other operations run in the temporary environment
3. **Change Review**: At the end of each interaction, you'll see a diff showing proposed changes
4. **Approval Prompt**: You'll be asked whether to apply changes to your working directory
5. **Cleanup**: Temporary files are automatically cleaned up when the session ends (for git repositories, the temporary worktree and its temporary branch are removed).

### Example Interaction

````
Running in shadow mode in /tmp/tmp123abc...

[After agent operations complete]

Proposed changes (Shadow Mode):
```diff
+++ src/auth.py
@@ -10,6 +10,8 @@
 def authenticate_user(username, password):
+    # Add input validation
+    if not username or not password:
+        raise ValueError("Username and password are required")
     return verify_credentials(username, password)

Would you like to apply these changes? ([yes]/no)

> yes

Great! I've applied the changes. What would you like to do next?
````

## Requirements and Limitations

### Git Repositories

- **Supported**: All git repositories
- **Preserves**: Uncommitted changes, untracked files
- **Requirements**: Git must be available in your PATH

### Non-Git Workspaces

- **File Limit**: Maximum 1000 files in the workspace
- **Supported**: Any directory structure under the file limit
- **Tracking**: Uses file system monitoring to detect changes

### MCP Servers

- **Limitation**: Cannot start shadow mode when MCP servers are already running
- **Resolution**: Stop MCP servers before enabling shadow mode
- **Behavior**: When shadow mode is active, any MCP servers launched by the agent will run with their working directory set to the temporary shadow workspace. This ensures tools operate on the isolated copy.

## Troubleshooting

### "Cannot start shadow mode when MCP servers are running"

**Solution**: Stop any running MCP servers using `/mcp` command before enabling shadow mode.

### "Shadow mode is only supported for git repositories and workspaces with 1000 or fewer files"

**Solution**: Either initialize a git repository in your workspace or reduce the number of files.

### Changes not applying correctly

**Issue**: Git patches may fail if there are conflicts
**Solution**: Commit or stash your working changes before enabling shadow mode
