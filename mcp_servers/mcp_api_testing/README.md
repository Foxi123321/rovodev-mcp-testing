# API Testing MCP Server

MCP server for API schema validation, request/response recording, and replay functionality.

## Features

- **Record API Calls**: Store request/response pairs for later analysis
- **Replay & Compare**: Replay recorded calls and detect differences
- **Schema Validation**: Validate responses against JSON schemas
- **Schema Drift Detection**: Compare API responses to detect breaking changes
- **Tag-Based Organization**: Filter recordings by tags and methods

## Tools

### record_api_call
Record an API request and response for later replay.

**Parameters:**
- `method` (required): HTTP method (GET, POST, etc)
- `url` (required): API endpoint URL
- `request_headers` (optional): Request headers
- `request_body` (optional): Request body
- `response_status` (required): HTTP status code
- `response_headers` (optional): Response headers
- `response_body` (required): Response body
- `tags` (optional): Tags for categorization

**Returns:** Recording ID and filepath

### replay_api_call
Replay a recorded API call and compare with expected response.

**Parameters:**
- `request_id` (required): ID of recorded request
- `actual_response` (required): New response to compare

**Returns:** Comparison results with differences

### validate_response
Validate an API response against a saved schema.

**Parameters:**
- `response` (required): Response to validate
- `schema_name` (required): Name of schema to validate against

**Returns:** Validation result with errors if any

### save_schema
Save an API response schema for validation.

**Parameters:**
- `name` (required): Schema name
- `schema` (required): JSON Schema definition

**Returns:** Schema filepath

### list_recordings
List all recorded API calls with optional filtering.

**Parameters:**
- `tags` (optional): Filter by tags
- `method` (optional): Filter by HTTP method

**Returns:** List of recordings

### get_recording
Get full details of a specific recording.

**Parameters:**
- `request_id` (required): Recording ID

**Returns:** Complete recording details

### detect_schema_drift
Compare two API responses to detect schema changes.

**Parameters:**
- `baseline_response` (required): Original response
- `current_response` (required): Current response

**Returns:** Detected differences and schema comparison

## Usage Example

```python
# Record an API call
record_api_call(
    method="GET",
    url="https://api.example.com/users/123",
    response_status=200,
    response_body={"id": 123, "name": "John"},
    tags=["users", "production"]
)

# Validate response against schema
save_schema(
    name="user_response",
    schema={
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    }
)

validate_response(
    response={"id": 123, "name": "John"},
    schema_name="user_response"
)

# Detect schema drift
detect_schema_drift(
    baseline_response={"id": 123, "name": "John"},
    current_response={"id": 123, "name": "John", "email": "john@example.com"}
)
# Returns: Fields added: email
```

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python server.py
```

Or add to your MCP config:

```json
{
  "mcpServers": {
    "api-testing": {
      "command": "python",
      "args": ["path/to/mcp_api_testing/server.py"]
    }
  }
}
```
