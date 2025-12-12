---
title: Manage Rovo Dev CLI Configuration
description: Learn how to configure Rovo Dev CLI using YAML with examples and best practices.
platform: platform
product: rovodev-cli
category: devguide
subcategory: configuration
date: '2025-11-05'
---
# Manage Rovo Dev CLI Configuration

Rovo Dev CLI can be customized through a configuration file to tailor its behavior to your preferences and workflow requirements.

## Opening the Configuration File

To access and edit your Rovo Dev CLI configuration, use the config command:

```bash
acli rovodev config
```

This command opens the configuration file in your default editor. The configuration file is located at `~/.rovodev/config.yml` by default, but you can specify a custom location using the `--config-file` flag when running Rovo Dev.

## Configuration Structure

The configuration file uses YAML format with a hierarchical structure. All configuration options are optional and will use sensible defaults if not specified.

### Agent Configuration

Control how the AI agent behaves and responds:

```yaml
agent:
  # Additional system prompt to append to the agent's default system prompt
  additionalSystemPrompt: "Always prioritize code readability and maintainability."

  # Enable streaming responses from the AI model (default: true)
  streaming: true

  # Temperature setting for AI model responses (0.0-1.0, default: 0.3)
  temperature: 0.3

  # Model ID to use for the agent (default: "auto")
  modelId: "auto"

  # Enable the deep planning tool for complex task planning (default: false)
  enableDeepPlanTool: false

  experimental:
    # Enable shadow mode - run on temporary workspace clone (default: false)
    enableShadowMode: false

    # (internal) Disable the built-in Atlassian MCP server so you can configure a custom one
    disableBuiltinAtlassianMcp: false
```

### Sessions Configuration

Manage session behavior and storage:

```yaml
sessions:
  # Automatically restore the last active session on startup (default: false)
  autoRestore: false

  # Directory where session data is stored (default: ~/.rovodev/sessions)
  persistenceDir: "~/.rovodev/sessions"
```

### Atlassian Connections

Configure integration with Atlassian products:

```yaml
atlassianConnections:
  # Global Jira projects user is part of
  jiraProjects:
    - url: "https://yoursite.atlassian.net/browse/PROJ"
      key: "PROJ"
      id: "your-project-id"

  # Path to project-level override file (default: .rovodev/atlassian_connections.json)
  localOverridePath: ".rovodev/atlassian_connections.json"

  # Whether Atlassian integration is enabled (default: true)
  enabled: true
```

### Console Configuration

Customize the console display and interaction:

```yaml
console:
  # Output format for console display (default: "markdown")
  # Options: "markdown", "simple", "raw"
  outputFormat: "markdown"

  # Show tool execution results in the console (default: true)
  showToolResults: true

  # Editing mode for the prompt session (default: "EMACS")
  # Options: "EMACS", "VI"
  editingMode: "EMACS"

  # Shell command to generate a custom command prompt that replaces the default '> '
  # For example: set 'STARSHIP_SHELL=rovodev starship prompt' to use Starship (default: null)
  customCommandPrompt: null

  # Maximum width of console output in characters, or "fill" (default: 120)
  maxOutputWidth: 120
```

### Logging Configuration

Control logging behavior:

```yaml
logging:
  # Path to the log file (default: ~/.rovodev/rovodev.log)
  path: "~/.rovodev/rovodev.log"

  # Enable collection of prompts for debugging (internal users only)
  enablePromptCollection: false
```

### MCP (Model Context Protocol) Configuration

Configure MCP servers and protocols:

```yaml
mcp:
  # Path to the MCP configuration file (default: ~/.rovodev/mcp.json)
  mcpConfigPath: "~/.rovodev/mcp.json"

  # List of allowed MCP server signatures
  allowedMcpServers: []

  # List of globally disabled MCP server signatures
  disabledMcpServers: []
```

### Tool Permissions

Control which tools can be executed and how:

```yaml
toolPermissions:
  # Default permission for tools not explicitly listed (default: "ask")
  # Options: "allow", "ask", "deny"
  default: "ask"

  # Permission settings for specific tools
  tools:
    # File operations
    create_file: "ask"
    delete_file: "ask"
    move_file: "ask"
    find_and_replace_code: "ask"

    # Safe read operations
    open_files: "allow"
    expand_code_chunks: "allow"
    expand_folder: "allow"
    grep: "allow"

    # Planning tools
    # Note: tool names are case-sensitive and must match exactly
    create_technical_plan: "allow"

    # Atlassian integration tools
    getJiraIssue: "allow"
    createJiraIssue: "ask"
    updateJiraIssue: "ask"
    getConfluencePage: "allow"
    createConfluencePage: "ask"
    updateConfluencePage: "ask"

  # Bash command permissions
  # Note: On Windows, use 'powershell' instead of 'bash' here
  bash:
    # Default permission for bash commands (default: "ask")
    default: "ask"

    # Specific bash commands with permissions
    commands:
      - command: "ls.*"
        permission: "allow"
      - command: "cat.*"
        permission: "allow"
      - command: "echo.*"
        permission: "allow"
      - command: "pwd"
        permission: "allow"

    # Run commands in a sandboxed environment (macOS and Linux only). On Windows, enabling this disables PowerShell commands.
    runInSandbox: false

  # File/directory paths allowed outside workspace
  allowedExternalPaths: []
```

### Announcement Tracking

Internal configuration for tracking announcement displays:

```yaml
announcementTracking:
  # Dictionary mapping announcement text hash to display count
  announcementViewCounts: {}
```

### Atlassian Billing Site

Configuration for Atlassian billing site information:

```yaml
atlassianBillingSite:
  siteUrl: "https://yoursite.atlassian.net"
  # (deprecated) cloudId is accepted for backward compatibility but ignored
```

### Smart Tasks

Configure Smart Tasks discovery and display:

```yaml
smartTasks:
  # Enable Smart Tasks discovery (default: true)
  enabled: true
  # Task discovery sources (default: ["filesystem"]) 
  sources: ["filesystem"]
```

### Session Feedback Preferences

Control whether the CLI asks for session success feedback:

```yaml
sessionFeedback:
  # Permanently disable feedback prompts (default: false)
  permanentlyDisabled: false
  # ISO timestamp of when feedback was last asked (managed by CLI)
  lastFeedbackAsked: null
```

## Example Configuration

Here's a complete example configuration file:

```yaml
version: 1
agent:
  additionalSystemPrompt: "Focus on clean, maintainable code with comprehensive error handling."
  streaming: true
  temperature: 0.2
  modelId: "auto"
  enableDeepPlanTool: true

sessions:
  autoRestore: true
  persistenceDir: "~/.rovodev/sessions"

atlassianConnections:
  jiraProjects:
    - url: "https://mycompany.atlassian.net/browse/PROJ"
      key: "PROJ"
      id: "12345"
  enabled: true

console:
  outputFormat: "markdown"
  showToolResults: true
  editingMode: "EMACS"
  customCommandPrompt: null
  maxOutputWidth: "fill"

logging:
  path: "~/.rovodev/rovodev.log"

mcp:
  mcpConfigPath: "~/.rovodev/mcp.json"

smartTasks:
  enabled: true
  sources: ["filesystem"]

sessionFeedback:
  permanentlyDisabled: false
  lastFeedbackAsked: null

toolPermissions:
  default: "ask"
  tools:
    open_files: "allow"
    expand_code_chunks: "allow"
    grep: "allow"
    create_file: "ask"
    delete_file: "deny"
  bash:
    default: "ask"
    commands:
      - command: "git .*"
        permission: "allow"
      - command: "npm .*"
        permission: "ask"
```

## Tips for Configuration

- **Start simple**: Begin with a minimal configuration and add options as needed
- **Use path expansion**: Paths support `~` for home directory expansion
- **Permission levels**: Use "allow" for safe operations, "ask" for potentially destructive ones, and "deny" to block entirely
- **Tool permissions**: Configure permissions based on your security requirements and workflow
- **Backup your config**: Keep a backup of your configuration file, especially if you have custom tool permissions

## Troubleshooting

- **Invalid configuration**: If the config file has errors, Rovo Dev will warn you about unknown fields
- **Path issues**: Ensure all file and directory paths are accessible and use proper path separators for your OS
- **Permission conflicts**: If you encounter permission issues, check your `toolPermissions` settings
- **Missing config**: If no config file exists, Rovo Dev will create one with default settings when you run `acli rovodev config`
