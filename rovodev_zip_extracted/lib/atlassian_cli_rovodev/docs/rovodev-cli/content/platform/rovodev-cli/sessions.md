---
title: Sessions
description: Manage session history, forking, renaming, restoration, and best practices in Rovo Dev CLI.
platform: platform
product: rovodev-cli
category: devguide
subcategory: using-the-cli
date: '2025-12-02'
---
# Sessions

Sessions in Rovo Dev CLI allow you to maintain conversation history and context across multiple interactions. Each session preserves your conversation state, enabling you to continue work where you left off and maintain context between different coding tasks.

## Overview

Sessions provide:

- **Context Preservation**: Each session maintains its own message history and conversation context
- **Workspace Isolation**: Sessions are tied to specific workspaces for better organization
- **Persistent Storage**: Sessions are automatically saved and can be restored when you restart Rovo Dev
- **Session Management**: Create, switch between, fork, and rename sessions as needed

## Session Commands

### Core Session Management

- **`/sessions`** - Open the interactive session menu to view, switch, and manage sessions
- **`/sessions new [title]`** - Create a new session with optional custom title
- **`/sessions fork [title]`** - Fork the current session with optional custom title
- **`/sessions rename <new_title>`** - Rename the current session
- **`/sessions rename <session_id> <new_title>`** - Rename a specific session

### Session Menu Interface

The `/sessions` command opens an interactive menu that displays:

Note: The interactive menu does not support entering custom titles yet. Use `/sessions new "<title>"`, `/sessions fork "<title>"`, or `/sessions rename ...` to set custom titles.

- **Session List**: All sessions for the current workspace, sorted by last activity (forked sessions are grouped under their parent)
- **Session Details**: Message count, creation date, token usage, and conversation preview
- **Navigation**: Use arrow keys to navigate, Enter to select, and hotkeys for actions

#### Session Menu Hotkeys

- **↑ ↓**: Navigate between sessions
- **Enter**: Switch to selected session
- **n**: Create a new session
- **f**: Fork the selected session
- **d**: Delete the selected session (with confirmation; cannot delete the only remaining session)
- **q**: Quit without making changes
### Session Information Display

For each session, the menu shows:

- **Title**: Session name (auto-generated or custom)
- **Messages**: Total number of messages in the conversation
- **Last Activity**: When the session was last modified
- **Context Usage**: Visual bar showing token usage relative to context limit
- **Conversation Preview**: Initial prompt and latest response excerpt

## Working with Sessions

### Creating Sessions

**New Session with Default Title:**

```
/sessions new
```

**New Session with Custom Title:**

```
/sessions new "Bug Fix Session"
/sessions new "Feature Development - User Auth"
```

### Forking Sessions

Forking creates a copy of the current session with all its conversation history. The forked session keeps all messages but its initial prompt is cleared:

**Fork with Default Title:** (defaults to "Fork of {original_title}")

```
/sessions fork
```

**Fork with Custom Title:**

```
/sessions fork "Experiment with different approach"
/sessions fork "Alternative implementation"
```

### Renaming Sessions

Title rules:
- Titles must be non-empty and at most 100 characters
- Custom (manual) titles are preserved and won't be overwritten by auto-generated titles

**Rename Current Session:**

```
/sessions rename "Updated Session Name"
```

**Rename Specific Session:**

```
/sessions rename abc123-def456 "Code Review Session"
```

### Session Restoration

Sessions can be restored when restarting Rovo Dev. Restoration is scoped to the current workspace:

- When restoring, Rovo Dev selects the most recently active session for the current workspace.
- If there are no sessions for the current workspace, a new session will be started instead.

**Continue Last Session (current workspace):**

```bash
acli rovodev run --restore
```

**Auto-restore (via config):**
Enable `sessions.autoRestore` in your config file to automatically continue the last session for the current workspace.

**Note:** The `sessions.autoRestore` config setting is deprecated. Use the `--restore` flag instead.

## Session Organization

### Workspace-Based Organization

Sessions are automatically organized by workspace:

- Each workspace maintains its own set of sessions
- Sessions created in a workspace are only visible when working in that workspace
- This provides natural isolation between different projects

Note: Legacy sessions created before workspace tracking may appear in all workspaces until metadata is updated.

### Session Hierarchy

When you fork a session, it creates a parent-child relationship:

- Forked sessions show as nested under their parent in the session list
- The display uses indentation to show the relationship hierarchy
- Deleting a parent session doesn't affect its children

### Session Titles

- **Auto-generated**: Default titles are created automatically based on conversation content
- **Custom Titles**: You can provide custom titles when creating or renaming sessions
- **Manual Override**: Custom titles are preserved and won't be overwritten by auto-generation

## Session Storage

Sessions are stored in your persistence directory (typically `~/.rovodev/sessions/`) with:

- **session_context.json**: Contains the full conversation history and context
- **metadata.json**: Stores session metadata like title, workspace path, and fork information

Configuration:
- You can change the storage location via `sessions.persistence_dir` in your config file.

## Best Practices

### When to Create New Sessions

- **Different Tasks**: Start a new session for each distinct coding task or feature
- **Context Switch**: Create a new session when switching between unrelated work
- **Experimentation**: Fork sessions when trying different approaches to the same problem

### Session Management Tips

- **Use Descriptive Titles**: Custom titles help identify sessions quickly
- **Regular Cleanup**: Delete old sessions that are no longer needed
- **Fork for Experiments**: Use forking to try different approaches without losing your main progress
- **Restore Sessions**: Use `--restore` to continue where you left off

### Performance Considerations

- **Large Sessions**: Sessions with extensive history may load slower
- **Token Limits**: Monitor context usage to avoid hitting model token limits
- **Storage Space**: Very large sessions (roughly >20MB after cleanup) are automatically skipped to prevent performance issues. If sessions are skipped, a warning will be shown in the CLI; check logs using `acli rovodev log` for details.

## Integration with Other Features

### Session History Management

- **`/clear`** - Clear the current session's message history (cannot be undone)
- **`/prune`** - Reduce token size while retaining context (removes tool results)

### Copy Commands

- **`/copy`** - Copy the last agent response from the current session
- **`/copy conversation [limit]`** - Copy conversation history to clipboard
