# Rovo Dev ACP Mode

## Overview

Rovo Dev ACP (Agent Code Protocol) mode enables Rovo Dev to function as an agent server that can be integrated with code editors and IDEs that support the ACP specification. ACP is a protocol for connecting AI agents to development environments, allowing real-time code analysis, generation, and manipulation.

In ACP mode, Rovo Dev runs as a server that listens for requests from your editor and provides intelligent code assistance through a standardized protocol.

## Prerequisites

- **Rovo Dev CLI**: Ensure you have Rovo Dev CLI installed
- **ACP-Compatible Editor**: Your editor must support the Agent Code Protocol
- **Configuration**: A valid Rovo Dev configuration file (see [Configuration](#configuration))

## Starting ACP Server

To start Rovo Dev in ACP mode, use the following command:

```bash
uv run rovodev acp
```

### Optional Parameters

- `--config-file`: Path to a custom configuration file (defaults to `~/.rovodev/config.yml`)
- `--site-url`: Specify an Atlassian site URL for Jira/Confluence integration

#### Examples

```bash
# Start ACP server with custom config
uv run rovodev acp --config-file /path/to/custom/config.yml

# Start ACP server with specific Atlassian site
uv run rovodev acp --site-url https://your-site.atlassian.net
```

## Editor Integration

### Zed Editor

To add Rovo Dev as an agent server in Zed, add the following to your Zed settings file (`~/.config/zed/settings.json`):

```json
{
  "agent_servers": {
    "Rovo Dev": {
      "command": "acli",
      "args": [
        "rovodev",
        "acp"
      ]
    }
  }
}
```

### Neovim (via codecompanion.nvim)

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
    -- NOTE: The log_level is in `opts.opts`
    opts = {
      log_level = "DEBUG",
    },
  },
}
```
Replace `/path/to/your/acra-python` with the actual path to your project directory.

**Optional: Add custom configuration**

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

### Other Editors

If your editor supports ACP, follow these general steps:

1. Configure your editor to run the command: `acli rovodev acp`
2. Ensure the command is run from or has access to your project directory
3. The editor should automatically handle communication with the ACP server via stdio


## Features

- **Real-time Code Assistance**: Get instant feedback on code quality, suggestions, and improvements
- **Integrated Tools**: Access to file manipulation, terminal execution, and more
- **MCP Server Support**: Use Model Context Protocol servers for extended functionality
- **Atlassian Integration**: Direct access to Jira issues and Confluence pages through configured connections
- **Model Selection**: Support for multiple AI models with automatic fallback capabilities
- **Streaming Responses**: Real-time streaming of agent responses for faster feedback

## Related Documentation

- [Rovo Dev Main Documentation](../../../README.md)
- [Agent Code Protocol Introduction](https://agentclientprotocol.com/overview/introduction)
