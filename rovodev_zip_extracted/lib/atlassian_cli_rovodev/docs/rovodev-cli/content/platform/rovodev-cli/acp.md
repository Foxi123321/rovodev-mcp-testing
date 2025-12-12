---
title: ACP (Agent Client Protocol)
description: Run Rovo Dev as an Agent Client Protocol server for integration with code editors and IDEs
date: 2025-01-23
subcategory: using-the-cli
---

# ACP (Agent Client Protocol)

The Agent Client Protocol (ACP) is an open standard that enables communication between code editors/IDEs and AI coding agents. Rovo Dev implements ACP, allowing it to function as an agent server that integrates seamlessly with ACP-compatible editors.

## Overview

When running in ACP mode, Rovo Dev operates as a subprocess of your code editor, communicating via JSON-RPC over stdio. This integration provides:

- **Real-time code assistance**: Get instant feedback on code quality, suggestions, and improvements
- **Integrated tools**: Access to file manipulation, terminal execution, and workspace exploration
- **MCP server support**: Use Model Context Protocol servers for extended functionality
- **Atlassian integration**: Direct access to Jira issues and Confluence pages
- **Model selection**: Support for multiple AI models with automatic fallback capabilities
- **Streaming responses**: Real-time streaming of agent responses for faster feedback

## Starting the ACP Server

**(internal)** The ACP command is currently an internal-only feature.

To start Rovo Dev in ACP mode:

```bash
acli rovodev acp
```

### Command Options

- `--config-file`: Path to a custom configuration file (default: `~/.rovodev/config.yml`)
- `--site-url`: Specify an Atlassian site URL for Jira/Confluence integration

### Examples

```bash
# Start with custom config
acli rovodev acp --config-file /path/to/custom/config.yml

# Start with specific Atlassian site
acli rovodev acp --site-url https://your-site.atlassian.net
```

## Editor Integration

### Zed Editor

Add the following to your Zed settings file (`~/.config/zed/settings.json`):

```json
{
  "agent_servers": {
    "Rovo Dev": {
      "command": "acli",
      "args": ["rovodev", "acp"]
    }
  }
}
```

#### With Custom Configuration

```json
{
  "agent_servers": {
    "Rovo Dev": {
      "command": "acli",
      "args": [
        "rovodev",
        "acp",
        "--config-file",
        "/path/to/custom/config.yml"
      ]
    }
  }
}
```

### Neovim (via codecompanion.nvim)

Add the following configuration to your Neovim setup:

```lua
return {
  "olimorris/codecompanion.nvim",
  dependencies = {
    "nvim-lua/plenary.nvim",
  },
  opts = {
    adapters = {
      acp = {
        rovodev = function()
          local helpers = require("codecompanion.adapters.acp.helpers")
          return {
            name = "rovodev",
            type = "acp",
            formatted_name = "RovoDev",
            roles = {
              llm = "assistant",
              user = "user",
            },
            opts = {
              verbose_output = true,
            },
            commands = {
              default = {
                "acli",
                "rovodev",
                "acp",
              },
            },
            defaults = {},
            parameters = {
              protocolVersion = 1,
              clientCapabilities = {
                fs = { readTextFile = true, writeTextFile = true },
              },
              clientInfo = {
                name = "CodeCompanion.nvim",
                version = "1.0.0",
              },
            },
            handlers = {
              setup = function(self)
                return true
              end,
              form_messages = function(self, messages, capabilities)
                return helpers.form_messages(self, messages, capabilities)
              end,
              on_exit = function(self, code) end,
            },
          }
        end,
      },
    },
    strategies = {
      chat = {
        adapter = "rovodev",
      },
      inline = {
        adapter = "rovodev",
      },
      cmd = {
        adapter = "rovodev",
      },
    },
    opts = {
      log_level = "DEBUG",
    },
  },
}
```

### Other Editors

If your editor supports ACP:

1. Configure your editor to run the command: `acli rovodev acp`
2. Ensure the command is run from or has access to your project directory
3. The editor should automatically handle communication with the ACP server via stdio

## Features

### Agent Capabilities

- **Session management**: Create and load sessions with persistent context
- **Model selection**: Choose from available AI models and persist your selection
- **Agent modes**: Switch between different operational modes:
  - **Default**: Balanced mode with standard permissions
  - **Ask**: Prompts for approval before making changes
  - **Yolo**: Allows all file operations and bash commands without asking

### Tool Integration

Rovo Dev's ACP implementation provides rich integration with various tools:

- **File operations**: Read, write, create, delete, and move files with diff visualization
- **Terminal commands**: Execute bash and PowerShell commands with output streaming
- **Code navigation**: Expand code chunks, search patterns, and explore workspace structure
- **Git operations**: Access commit history and change patches
- **MCP servers**: Connect to Model Context Protocol servers for extended capabilities

### Permission Management

The ACP implementation includes intelligent permission management:

- Request permissions for sensitive operations (file changes, terminal commands)
- Support for one-time, session-scoped, and persistent permissions
- Pattern-based permissions for command families
- Visual permission prompts in your editor

### Prompt Commands

Use `/prompt:<name>` to invoke custom prompts defined in your `prompts.yml` configuration. Available prompts are automatically registered as commands in the editor.

## Related Resources

- [Agent Client Protocol - Introduction](https://agentclientprotocol.com/overview/introduction)
- [Agent Client Protocol - Clients](https://agentclientprotocol.com/overview/clients)
- [Config file](/platform/rovodev-cli/config/)
- [Tool permissions](/platform/rovodev-cli/permissions/)
