---
title: V3 API Reference
description: V3 API Reference
platform: platform
product: rovodev-cli
category: devguide
subcategory: serve
date: '2025-12-01'
---

# V3 API Reference

The V3 API provides enhanced chat functionality with fine-grained control over tool execution, including the ability to pause and approve/deny tool calls before execution.

**Base URL**: `http://localhost:8123/v3/`

## Authentication

All V3 API endpoints require Bearer token authentication. Include the session token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer <session-token>" \
     -H "Content-Type: application/json" \
     -d '{"initial_message": "Hello"}' \
     http://localhost:8123/v3/sessions/create
```

## Key Differences from V2

- **Separated Message Setting**: Use `/set_chat_message` to set the message, then `/stream_chat` to execute
- **Tool Execution Control**: Pause on tool calls and approve/deny them individually
- **Enhanced Workflow**: Better suited for applications requiring human oversight of tool execution
- **Context Support**: Full support for context items (same as V2) in `/set_chat_message`

## Endpoints

### Agent Lifecycle Events

#### GET /v3/agent_lifecycle_events
Stream agent run lifecycle events as Server-Sent Events.

Events:
- `agent_run_start`: Emitted when an agent run starts
- `agent_run_end`: Emitted when an agent run ends (includes task classification data)
- `error`: Emitted when an error occurs

Event data payload example:
```json
{
  "timestamp": 1734312345.123,
  "session_id": "<uuid>",
  "task_status": "TASK_COMPLETED" | "WAITING_FOR_USER",
  "error_message": "string (optional)",
  "error_type": "string (optional)"
}
```

Example:
```bash
curl http://localhost:8123/v3/agent_lifecycle_events --no-buffer
```

### Chat Workflow

#### POST /v3/set_chat_message
Set the chat message to be processed by stream_chat.

**Request Body:**
```json
{
  "message": "string",           // Required: The user's message
  "context": [                   // Optional: Context items to provide additional information
    {
      "type": "note",            // Generic context item
      "content": "string"        // Content of the context item
    },
    {
      "type": "file",            // File context item
      "file_path": "string",     // Path to the file
      "selection": {             // Optional: Specific lines in the file
        "start": 10,             // Start line number
        "end": 20                // End line number
      },
      "note": "string"           // Optional: Description of the file/selection
    }
  ],
  "enable_deep_plan": false      // Optional: Enable technical planning (default: false)
}
```

**Response:**
```json
{
  "response": "Chat message set"  // or "Chat message cleared" if message is empty
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/set_chat_message \
  -H "Content-Type: application/json" \
  -d '{"message": "List files in the project", "enable_deep_plan": false}' | jq .
```

**Example with Context:**
```bash
curl -X POST http://localhost:8123/v3/set_chat_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Review this code for security issues",
    "context": [
      {
        "type": "instruction",
        "content": "Focus on input validation and authentication"
      },
      {
        "type": "file",
        "file_path": "src/auth/login.py",
        "selection": {
          "start": 25,
          "end": 50
        },
        "note": "Login validation function"
      }
    ],
    "enable_deep_plan": true
  }' | jq .
```

#### GET /v3/stream_chat
Stream chat response for the currently set message.

**Parameters:**
- `pause_on_call_tools_start` (query, optional): Whether to pause when tool execution starts

**Response**: Server-Sent Events stream

**Example:**
```bash
# Basic streaming
curl http://localhost:8123/v3/stream_chat --no-buffer

# With tool execution pausing
curl "http://localhost:8123/v3/stream_chat?pause_on_call_tools_start=true" --no-buffer
```

**Error Responses:**
- **400**: No chat message set (use `/set_chat_message` first)
- **409**: Chat already in progress

#### POST /v3/resume_tool_calls
Resume tool calls that were paused during stream_chat.

**Request Body:**
```json
{
  "decisions": [
    {
      "tool_call_id": "string",           // Required: Tool call ID from pause event
      "deny_message": "string" | null     // Optional: If provided, denies the tool call
    }
  ]
}
```

**Response:**
```json
{
  "message": "resume_tool_calls done"
}
```

**Example:**
```bash
# Approve all tool calls
curl -X POST http://localhost:8123/v3/resume_tool_calls \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": [
      {
        "tool_call_id": "toolu_vrtx_01CtgADk2XWPu4jhKVwiKaeP",
        "deny_message": null
      }
    ]
  }' | jq .

# Deny a tool call
curl -X POST http://localhost:8123/v3/resume_tool_calls \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": [
      {
        "tool_call_id": "toolu_vrtx_01CtgADk2XWPu4jhKVwiKaeP",
        "deny_message": "File operation not approved"
      }
    ]
  }' | jq .
```

#### POST /v3/replay
Replay endpoint to stream buffered chat events and continue streaming new ones.

**Response**: Server-Sent Events stream

**Example:**
```bash
curl -X POST http://localhost:8123/v3/replay --no-buffer
```

### Session Management

#### GET /v3/sessions/list
List all available sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_context": {
        "id": "string",
        "message_history": null,
        "usage": {
          "requests": 0,
          "input_tokens": 0,
          "output_tokens": 0,
          "total_tokens": 0,
          "details": {}
        },
        "timestamp": 0,
        "initial_prompt": "string",
        "prompts": ["string"],
        "latest_result": "string",
        "workspace_path": "string",
        "log_dir": "string"
      },
      "title": "string",
      "last_saved": "string",
      "context_limit": 200000,
      "path": "string",
      "parent_session_id": null,
      "num_messages": 0
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8123/v3/sessions/list | jq .
```

#### GET /v3/sessions/current_session
Get information about the current session.

**Response:**
```json
{
  "session_context": {
    "id": "string",
    "usage": {
      "requests": 0,
      "input_tokens": 0,
      "output_tokens": 0,
      "total_tokens": 0
    },
    "timestamp": 0,
    "initial_prompt": "string",
    "workspace_path": "string"
  },
  "title": "string",
  "last_saved": "string",
  "num_messages": 0
}
```

**Example:**
```bash
curl http://localhost:8123/v3/sessions/current_session | jq .
```

#### POST /v3/sessions/create
Create a new session.

**Request Body (optional):**
```json
{
  "custom_title": "My Custom Session Title"  // Optional: Session title (default: "Untitled Session")
}
```

**Response:**
```json
{
  "session_id": "string",
  "title": "My Custom Session Title",
  "message": "Session created successfully"
}
```

**Status Codes:**
- `200`: Success
- `409`: Conflict - Chat in progress, cancel before creating new session

**Example:**
```bash
curl -X POST http://localhost:8123/v3/sessions/create | jq .
```

#### GET /v3/sessions/{session_id}
Get information about a specific session.

**Parameters:**
- `session_id` (path): The session ID

**Response**: Same as current_session

**Example:**
```bash
curl http://localhost:8123/v3/sessions/2480ebc2-9eaf-4597-9c19-5ed0b43b45f2 | jq .
```

#### POST /v3/sessions/{session_id}/restore
Restore a previous session.

**Parameters:**
- `session_id` (path): The session ID to restore

**Response:**
```json
{
  "session_id": "string",
  "message": "Session restored successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/sessions/2480ebc2-9eaf-4597-9c19-5ed0b43b45f2/restore | jq .
```

### Tool Management

#### GET /v3/tools
Get the list of available tools.

**Response:**
```json
[
  {
    "name": "string",
    "parameters_json_schema": {
      "type": "object",
      "properties": {},
      "required": []
    },
    "description": "string",
    "strict": boolean
  }
]
```

**Example:**
```bash
curl http://localhost:8123/v3/tools | jq .
```

#### POST /v3/tool
Execute a tool directly.

**Request Body:**
```json
{
  "tool_name": "string",        // Required: Name of the tool to execute
  "arguments": {}               // Required: Tool arguments as key-value pairs
}
```

**Response:**
```json
{
  "result": "string"           // Tool execution result
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "open_files",
    "arguments": {
      "file_paths": ["README.md"]
    }
  }' | jq .
```

### File Cache Management

#### GET /v3/cache-file-path
Get the cached file path for a given file.

**Parameters:**
- `file_path` (query): The file path to get cached version for

**Response:**
```json
{
  "cached_file_path": "string"
}
```

**Example:**
```bash
curl "http://localhost:8123/v3/cache-file-path?file_path=README.md" | jq .
```

#### POST /v3/invalidate-file-cache
Invalidate the cache by deleting all cached files.

**Response:**
```json
{
  "message": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/invalidate-file-cache | jq .
```

### Control Operations

#### POST /v3/cancel
Cancel any ongoing chat request.

**Response:**
```json
{
  "message": "string",
  "cancelled": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/cancel | jq .
```

#### POST /v3/reset
Reset the agent history and MCP servers. Also clears any set chat message.

**Response:**
```json
{
  "message": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/reset | jq .
```

#### POST /v3/clear
Clear the agent history and MCP servers. Equivalent to `/v3/reset`.

**Response:**
```json
{
  "message": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/clear | jq .
```

#### POST /v3/prune
Prune the agent message history to reduce context size.

**Response:**
```json
{
  "message": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:8123/v3/prune | jq .
```

#### GET /v3/status
Get the current status information including CLI version, working directory, account details, memory files, and model information.

**Response:**
```json
{
  "cliVersion": {
    "version": "string",
    "sessionId": "string"
  },
  "workingDirectory": "string",
  "account": {
    "email": "string",
    "accountId": "string",
    "orgId": "string", 
    "isServerAvailable": true
  },
  "memory": {
    "memoryPaths": ["string"],
    "hasMemoryFiles": true,
    "errorMessage": "string"
  },
  "model": {
    "modelName": "string",
    "humanReadableName": "string",
    "errorMessage": "string"
  }
}
```

**Status Codes:**
- `200`: Success

**Example:**
```bash
curl -X GET http://localhost:8123/v3/status | jq .
```

#### GET /v3/agent_lifecycle_events
Stream agent lifecycle events as Server-Sent Events.

This endpoint emits events during agent runs to help external systems track overall progress, completion, and errors. Unlike chat streaming, these events summarize lifecycle milestones.

- Event names: `agent_run_start`, `agent_run_end`, `error`
- Data payload always includes: `timestamp` (unix seconds), `session_id` (string)
- Additional fields vary by event type

**Response:** Server-Sent Events stream

**Event Schemas:**

- `agent_run_start`
  ```json
  {
    "timestamp": 0.0,
    "session_id": "string"
  }
  ```

- `agent_run_end`
  ```json
  {
    "timestamp": 0.0,
    "session_id": "string",
    "task_status": "TASK_COMPLETED" | "WAITING_FOR_USER",
    "error_message": "string | null"  
  }
  ```
  Notes:
  - `task_status` is derived from the last agent response and indicates whether the current task appears complete or awaiting more user input.

- `error`
  ```json
  {
    "timestamp": 0.0,
    "session_id": "string",
    "error_type": "string",
    "error_message": "string"
  }
  ```

**Example:**
```bash
curl -N http://localhost:8123/v3/agent_lifecycle_events --no-buffer
```

### Configuration

#### POST /v3/set-site-url
Set the user's Atlassian site URL used for billing, analytics, and product integration.

Request Body:
```json
{
  "site_url": "https://<your-site>.atlassian.net"
}
```

Response:
```json
{
  "message": "Site URL updated successfully to: https://<your-site>.atlassian.net"
}
```

Example:
```bash
curl -X POST http://localhost:8123/v3/set-site-url \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://hello.atlassian.net"
  }' | jq .
```

Notes:
- Persists the site URL into the user's CLI config file and takes effect for subsequent requests
- Equivalent to passing the CLI flag `--site-url` when starting the server
- Useful when the account has access to multiple Atlassian cloud sites and you need to select the billing site

## V3 Streaming Events

V3 uses the same streaming events as V2, with one additional event type:

### on_call_tools_start
Emitted when tool execution is paused for approval (when `pause_on_call_tools_start=true`).

**Schema:**
```json
{
  "parts": [
    {
      "tool_name": "string",
      "args": {},
      "tool_call_id": "string"
    }
  ],
  "timestamp": "2025-08-15T06:33:29.019496+00:00",
  "part_kind": "on_call_tools_start"
}
```

**Example:**
```
event: on_call_tools_start
data: {"parts": [{"tool_name": "open_files", "args": {"file_paths": ["README.md"]}, "tool_call_id": "toolu_vrtx_01CtgADk2XWPu4jhKVwiKaeP"}], "timestamp": "2025-08-15T06:33:29.019496+00:00", "part_kind": "on_call_tools_start"}
```

## Usage Workflows

### Basic V3 Chat Flow

```bash
# 1. Set the message
curl -X POST http://localhost:8123/v3/set_chat_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a new Python file", "enable_deep_plan": false}'

# 2. Stream the response
curl http://localhost:8123/v3/stream_chat --no-buffer
```

### Controlled Tool Execution Flow

```bash
# 1. Set the message
curl -X POST http://localhost:8123/v3/set_chat_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Delete the old config file", "enable_deep_plan": false}'

# 2. Stream with tool pausing
curl "http://localhost:8123/v3/stream_chat?pause_on_call_tools_start=true" --no-buffer

# 3. When you receive an on_call_tools_start event, decide whether to approve
# Approve the tool call:
curl -X POST http://localhost:8123/v3/resume_tool_calls \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": [
      {
        "tool_call_id": "toolu_vrtx_01CtgADk2XWPu4jhKVwiKaeP",
        "deny_message": null
      }
    ]
  }'

# Or deny the tool call:
curl -X POST http://localhost:8123/v3/resume_tool_calls \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": [
      {
        "tool_call_id": "toolu_vrtx_01CtgADk2XWPu4jhKVwiKaeP",
        "deny_message": "Deletion not approved by user"
      }
    ]
  }'
```

### Python Example with Tool Control

```python
import requests
import json

class V3ChatClient:
    def __init__(self, base_url="http://localhost:8123/v3"):
        self.base_url = base_url
        
    def set_message(self, message, enable_deep_plan=False):
        """Set the chat message."""
        response = requests.post(
            f"{self.base_url}/set_chat_message",
            json={"message": message, "enable_deep_plan": enable_deep_plan}
        )
        return response.json()
    
    def stream_chat(self, pause_on_tools=False, tool_approver=None):
        """Stream chat with optional tool approval."""
        url = f"{self.base_url}/stream_chat"
        if pause_on_tools:
            url += "?pause_on_call_tools_start=true"
            
        response = requests.get(url, stream=True)
        
        for line in response.iter_lines():
            if not line:
                continue
                
            line = line.decode('utf-8')
            
            if line.startswith('event: '):
                event_type = line[7:]
            elif line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    
                    if event_type == 'on_call_tools_start':
                        # Handle tool approval
                        decisions = []
                        for tool_call in data['parts']:
                            approve = True
                            deny_message = None
                            
                            if tool_approver:
                                approve, deny_message = tool_approver(tool_call)
                            
                            decisions.append({
                                "tool_call_id": tool_call['tool_call_id'],
                                "deny_message": deny_message if not approve else None
                            })
                        
                        self.resume_tool_calls(decisions)
                    
                    yield event_type, data
                    
                except json.JSONDecodeError:
                    continue
    
    def resume_tool_calls(self, decisions):
        """Resume tool calls with approval decisions."""
        response = requests.post(
            f"{self.base_url}/resume_tool_calls",
            json={"decisions": decisions}
        )
        return response.json()

# Usage example
def tool_approver(tool_call):
    """Example tool approver function."""
    tool_name = tool_call['tool_name']
    args = tool_call['args']
    
    print(f"Tool: {tool_name}")
    print(f"Args: {args}")
    
    # Auto-approve read operations, ask for write operations
    if tool_name in ['open_files', 'grep', 'bash']:
        if tool_name == 'bash' and any(cmd in str(args) for cmd in ['rm', 'delete', 'mv']):
            approval = input("Approve destructive bash command? (y/n): ").lower() == 'y'
            return approval, None if approval else "Destructive command denied"
        return True, None
    
    approval = input(f"Approve {tool_name}? (y/n): ").lower() == 'y'
    return approval, None if approval else "Tool execution denied by user"

# Example usage
client = V3ChatClient()
client.set_message("Clean up the project by removing old files")

for event_type, data in client.stream_chat(pause_on_tools=True, tool_approver=tool_approver):
    if event_type == 'part_delta' and data.get('delta', {}).get('part_delta_kind') == 'text':
        print(data['delta']['content_delta'], end='', flush=True)
```

### Configuration

#### POST /v3/set-site-url
Set the Atlassian site URL for billing and integration purposes.

**Request Body:**
```json
{
  "site_url": "https://hello.atlassian.net"
}
```

**Response:**
```json
{
  "response": "Site URL set successfully"
}
```

**Usage:**
```bash
curl -X POST http://localhost:8123/v3/set-site-url \
  -H "Content-Type: application/json" \
  -d '{"site_url": "https://hello.atlassian.net"}'
```

This endpoint is equivalent to using the `--site-url` command-line flag when starting the server.

## Error Handling

V3 API includes the same error responses as V2, plus:

**400 Bad Request (No Message Set):**
```json
{
  "detail": "No chat message set. Use set_chat_message first."
}
```

This occurs when calling `/stream_chat` without first setting a message via `/set_chat_message`.

## Best Practices

1. **Always Set Message First**: Call `/set_chat_message` before `/stream_chat`
2. **Handle Tool Pausing**: When using `pause_on_call_tools_start=true`, always handle `on_call_tools_start` events
3. **Implement Tool Approval Logic**: Create clear approval criteria for different tool types
4. **Error Recovery**: Use `/reset` to clear both agent state and any set messages
5. **Security**: Use tool pausing for operations that modify files or execute system commands

## Global Endpoints

Response Headers

All responses from the Serve API include the header `X-Session-ID` containing the current session ID. This is useful for correlating requests, logs, and streamed events to a specific session across clients and retries.

These endpoints are available at the root level (not versioned) and work with both V2 and V3 APIs.

### Health Check

#### GET /healthcheck
Check the health status of the server and MCP servers.

**Response:**
```json
{
  "status": "healthy" | "unhealthy" | "entitlement check failed" | "pending user review",
  "version": "string",
  "detail": {
    "title": "string",
    "message": "string"
  } | null,
  "mcp_servers": {
    "server_name": "running" | "stopped" | "pending user review"
  } | null
}
```

**Status Values:**
- `healthy`: All systems operational
- `unhealthy`: One or more MCP servers stopped
- `entitlement check failed`: User entitlement validation failed
- `pending user review`: Third-party MCP servers require user approval

**Example:**
```bash
curl http://localhost:8123/healthcheck | jq .
```

### Status and Management

#### POST /shutdown
Gracefully shutdown the server.

**Response**: Plain text response
```
Shutting down
```

**Status Codes:**
- `200`: Success - Server is shutting down

**Example:**
```bash
curl -X POST http://localhost:8123/shutdown
```

**Notes:**
- This endpoint cancels any ongoing chat requests before shutting down
- The server will exit with code 0 after responding
- Use this for programmatic server shutdown

---

#### POST /accept-mcp-terms
Accept or deny terms for third-party MCP servers.

**Request Body:**
```json
{
  "servers": [
    {
      "server_name": "string",
      "decision": "accept" | "deny"
    }
  ],
  "accept_all": false  // Optional: Accept all pending servers
}
```

**Response:**
```json
{
  "message": "MCP servers updated successfully"
}
```

**Example:**
```bash
# Accept specific servers
curl -X POST http://localhost:8123/accept-mcp-terms \
  -H "Content-Type: application/json" \
  -d '{
    "servers": [
      {
        "server_name": "third-party-server",
        "decision": "accept"
      }
    ]
  }' | jq .

# Accept all pending servers
curl -X POST http://localhost:8123/accept-mcp-terms \
  -H "Content-Type: application/json" \
  -d '{"accept_all": true}' | jq .
```

**Notes:**
- This endpoint is only available when the server is running without entitlement issues
- Use `/healthcheck` to see which servers require approval
- Denied servers will not be loaded or available for tool execution
