---
title: Connect MCP Servers to Rovo Dev CLI
description: Configure and manage Model Context Protocol (MCP) servers for external tools and data sources.
platform: platform
product: rovodev-cli
category: devguide
subcategory: configuration
date: '2025-10-09'
---
# Connect MCP Servers to Rovo Dev CLI

Rovo Dev CLI supports Model Context Protocol (MCP) servers to extend its capabilities with external data sources and tools. MCP allows you to connect Rovo Dev to various services like databases, APIs, file systems, and other external resources.

## What is MCP?

MCP provides a standardized way to connect AI applications like Rovo Dev to:

- **Data sources**: Local files, databases, APIs
- **Tools**: Search engines, calculators, specialized utilities
- **Workflows**: Custom prompts, automation scripts

Think of MCP like a USB-C port for AI applications - it provides a universal way to connect to external systems.

## Managing MCP Servers

### Interactive MCP Management

Use the `/mcp` command in interactive mode to manage your MCP servers.

This opens an interactive interface where you can:

- View all configured MCP servers
- See their current status (running, stopped, failed)
- Enable or disable specific servers
- View available tools from each server

### MCP Configuration File

Rovo Dev CLI stores MCP server configurations in `~/.rovodev/mcp.json`.

You can edit this file directly or run `acli rovodev mcp` to open it in your default editor.

## Configuring MCP Servers

### Configuration File Structure

The MCP configuration file follows this structure:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "transport": "stdio"
    },
    "http-server": {
      "url": "https://example.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      },
      "transport": "http"
    },
    "sse-server": {
      "url": "https://example.com/mcp/sse",
      "transport": "sse"
    }
  }
}
```

### Transport Types

MCP supports three transport methods:

- **stdio**: Communication via standard input/output (most common)
- **http**: Communication via HTTP requests
- **sse**: Communication via Server-Sent Events

### Global Configuration

You can globally disable specific MCP servers in your main config file (`~/.rovodev/config.yml`):

```yaml
mcp:
  # Path to MCP configuration file
  mcpConfigPath: "~/.rovodev/mcp.json"

  # List of globally disabled MCP server signatures
  disabledMcpServers:
    - "server-name-to-disable"
```

## Troubleshooting

### Server Startup Issues

If an MCP server fails to start:

1. **Check Dependencies**: Ensure required tools are installed (e.g., `uvx`, `npm`, `node`)
2. **Verify Configuration**: Check syntax and required parameters in `mcp.json`
3. **Test Manually**: Try running the server command directly

### Authentication Problems

For servers requiring authentication:

- Ensure API keys and tokens are correctly configured
- Check that credentials have the necessary permissions
- Verify URL endpoints are accessible

### Permission Issues

Some MCP servers may require additional permissions:

- File system access for file-based servers
- Network access for API-based servers
- Environment variables for authentication

## Security Considerations

When configuring MCP servers:

- **Credential Security**: Store sensitive credentials as environment variables, not in configuration files
- **Network Access**: Be cautious with servers that access external networks
- **File Access**: Limit file system access to necessary directories
- **Trust**: Only install MCP servers from trusted sources


