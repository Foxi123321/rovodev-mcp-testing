#!/usr/bin/env python3
"""
API Testing MCP Server
Provides API schema validation, request/response recording, and replay functionality
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import asyncio

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    import mcp.server.stdio
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp")
    exit(1)

# Initialize server
app = Server("api-testing")

# Storage paths
RECORDINGS_DIR = Path(__file__).parent / "recordings"
SCHEMAS_DIR = Path(__file__).parent / "schemas"
RECORDINGS_DIR.mkdir(exist_ok=True)
SCHEMAS_DIR.mkdir(exist_ok=True)

def generate_request_id(method: str, url: str, body: Any = None) -> str:
    """Generate unique ID for request"""
    data = f"{method}:{url}:{json.dumps(body) if body else ''}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def save_recording(recording: dict) -> str:
    """Save API recording to file"""
    request_id = recording.get("request_id")
    filepath = RECORDINGS_DIR / f"{request_id}.json"
    
    with open(filepath, "w") as f:
        json.dump(recording, f, indent=2)
    
    return str(filepath)

def load_recording(request_id: str) -> Optional[dict]:
    """Load API recording from file"""
    filepath = RECORDINGS_DIR / f"{request_id}.json"
    
    if not filepath.exists():
        return None
    
    with open(filepath, "r") as f:
        return json.load(f)

def save_schema(name: str, schema: dict) -> str:
    """Save API schema"""
    filepath = SCHEMAS_DIR / f"{name}.json"
    
    with open(filepath, "w") as f:
        json.dump(schema, f, indent=2)
    
    return str(filepath)

def load_schema(name: str) -> Optional[dict]:
    """Load API schema"""
    filepath = SCHEMAS_DIR / f"{name}.json"
    
    if not filepath.exists():
        return None
    
    with open(filepath, "r") as f:
        return json.load(f)

def validate_against_schema(data: Any, schema: dict) -> dict:
    """Simple schema validation (basic type checking)"""
    errors = []
    
    if "type" in schema:
        expected_type = schema["type"]
        actual_type = type(data).__name__
        
        type_map = {
            "string": "str",
            "number": ["int", "float"],
            "integer": "int",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
            "null": "NoneType"
        }
        
        expected = type_map.get(expected_type, expected_type)
        
        if isinstance(expected, list):
            if actual_type not in expected:
                errors.append(f"Type mismatch: expected {expected}, got {actual_type}")
        else:
            if actual_type != expected:
                errors.append(f"Type mismatch: expected {expected}, got {actual_type}")
    
    if "properties" in schema and isinstance(data, dict):
        for key, prop_schema in schema["properties"].items():
            if key in data:
                result = validate_against_schema(data[key], prop_schema)
                errors.extend([f"{key}.{e}" for e in result["errors"]])
            elif schema.get("required") and key in schema["required"]:
                errors.append(f"Missing required field: {key}")
    
    if "items" in schema and isinstance(data, list):
        for i, item in enumerate(data):
            result = validate_against_schema(item, schema["items"])
            errors.extend([f"[{i}].{e}" for e in result["errors"]])
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available API testing tools"""
    return [
        Tool(
            name="record_api_call",
            description="Record an API request and response for later replay and validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE, etc)",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
                    },
                    "url": {
                        "type": "string",
                        "description": "API endpoint URL"
                    },
                    "request_headers": {
                        "type": "object",
                        "description": "Request headers (optional)"
                    },
                    "request_body": {
                        "type": ["object", "string", "null"],
                        "description": "Request body (optional)"
                    },
                    "response_status": {
                        "type": "integer",
                        "description": "HTTP response status code"
                    },
                    "response_headers": {
                        "type": "object",
                        "description": "Response headers (optional)"
                    },
                    "response_body": {
                        "type": ["object", "string", "null"],
                        "description": "Response body"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorizing recordings (optional)"
                    }
                },
                "required": ["method", "url", "response_status", "response_body"]
            }
        ),
        Tool(
            name="replay_api_call",
            description="Replay a recorded API call and compare with expected response",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID of the recorded request to replay"
                    },
                    "actual_response": {
                        "type": "object",
                        "description": "Actual response received from replay",
                        "properties": {
                            "status": {"type": "integer"},
                            "headers": {"type": "object"},
                            "body": {"type": ["object", "string", "null"]}
                        },
                        "required": ["status", "body"]
                    }
                },
                "required": ["request_id", "actual_response"]
            }
        ),
        Tool(
            name="validate_response",
            description="Validate API response against a schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "response": {
                        "type": ["object", "string"],
                        "description": "API response to validate"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Name of the schema to validate against"
                    }
                },
                "required": ["response", "schema_name"]
            }
        ),
        Tool(
            name="save_schema",
            description="Save an API response schema for validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Schema name (e.g., 'user_response', 'login_response')"
                    },
                    "schema": {
                        "type": "object",
                        "description": "JSON Schema definition"
                    }
                },
                "required": ["name", "schema"]
            }
        ),
        Tool(
            name="list_recordings",
            description="List all recorded API calls, optionally filtered by tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (optional)"
                    },
                    "method": {
                        "type": "string",
                        "description": "Filter by HTTP method (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_recording",
            description="Get details of a specific recorded API call",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID of the recording to retrieve"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="detect_schema_drift",
            description="Compare two API responses to detect schema changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "baseline_response": {
                        "type": ["object", "string"],
                        "description": "Original/baseline API response"
                    },
                    "current_response": {
                        "type": ["object", "string"],
                        "description": "Current API response to compare"
                    }
                },
                "required": ["baseline_response", "current_response"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "record_api_call":
            method = arguments["method"]
            url = arguments["url"]
            request_headers = arguments.get("request_headers", {})
            request_body = arguments.get("request_body")
            response_status = arguments["response_status"]
            response_headers = arguments.get("response_headers", {})
            response_body = arguments["response_body"]
            tags = arguments.get("tags", [])
            
            request_id = generate_request_id(method, url, request_body)
            
            recording = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "request": {
                    "method": method,
                    "url": url,
                    "headers": request_headers,
                    "body": request_body
                },
                "response": {
                    "status": response_status,
                    "headers": response_headers,
                    "body": response_body
                },
                "tags": tags
            }
            
            filepath = save_recording(recording)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "request_id": request_id,
                    "filepath": filepath,
                    "message": f"Recorded {method} {url}"
                }, indent=2)
            )]
        
        elif name == "replay_api_call":
            request_id = arguments["request_id"]
            actual_response = arguments["actual_response"]
            
            recording = load_recording(request_id)
            
            if not recording:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Recording not found: {request_id}"
                    }, indent=2)
                )]
            
            expected_response = recording["response"]
            
            # Compare responses
            differences = []
            
            if actual_response["status"] != expected_response["status"]:
                differences.append(f"Status code mismatch: expected {expected_response['status']}, got {actual_response['status']}")
            
            if actual_response["body"] != expected_response["body"]:
                differences.append("Response body differs from recorded")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "request_id": request_id,
                    "matches": len(differences) == 0,
                    "differences": differences,
                    "expected": expected_response,
                    "actual": actual_response
                }, indent=2)
            )]
        
        elif name == "validate_response":
            response = arguments["response"]
            schema_name = arguments["schema_name"]
            
            schema = load_schema(schema_name)
            
            if not schema:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Schema not found: {schema_name}"
                    }, indent=2)
                )]
            
            result = validate_against_schema(response, schema)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "schema_name": schema_name,
                    "valid": result["valid"],
                    "errors": result["errors"]
                }, indent=2)
            )]
        
        elif name == "save_schema":
            schema_name = arguments["name"]
            schema = arguments["schema"]
            
            filepath = save_schema(schema_name, schema)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "schema_name": schema_name,
                    "filepath": filepath
                }, indent=2)
            )]
        
        elif name == "list_recordings":
            filter_tags = arguments.get("tags", [])
            filter_method = arguments.get("method")
            
            recordings = []
            
            for filepath in RECORDINGS_DIR.glob("*.json"):
                with open(filepath, "r") as f:
                    recording = json.load(f)
                    
                    # Apply filters
                    if filter_tags:
                        if not any(tag in recording.get("tags", []) for tag in filter_tags):
                            continue
                    
                    if filter_method:
                        if recording["request"]["method"] != filter_method:
                            continue
                    
                    recordings.append({
                        "request_id": recording["request_id"],
                        "timestamp": recording["timestamp"],
                        "method": recording["request"]["method"],
                        "url": recording["request"]["url"],
                        "status": recording["response"]["status"],
                        "tags": recording.get("tags", [])
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(recordings),
                    "recordings": recordings
                }, indent=2)
            )]
        
        elif name == "get_recording":
            request_id = arguments["request_id"]
            
            recording = load_recording(request_id)
            
            if not recording:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Recording not found: {request_id}"
                    }, indent=2)
                )]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "recording": recording
                }, indent=2)
            )]
        
        elif name == "detect_schema_drift":
            baseline = arguments["baseline_response"]
            current = arguments["current_response"]
            
            def get_schema_structure(obj, path=""):
                """Extract schema structure from object"""
                if isinstance(obj, dict):
                    return {k: get_schema_structure(v, f"{path}.{k}") for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [get_schema_structure(obj[0], f"{path}[0]")] if obj else []
                else:
                    return type(obj).__name__
            
            baseline_schema = get_schema_structure(baseline)
            current_schema = get_schema_structure(current)
            
            # Find differences
            differences = []
            
            def compare_schemas(base, curr, path=""):
                if type(base) != type(curr):
                    differences.append(f"Type changed at {path}: {type(base).__name__} -> {type(curr).__name__}")
                elif isinstance(base, dict):
                    base_keys = set(base.keys())
                    curr_keys = set(curr.keys())
                    
                    added = curr_keys - base_keys
                    removed = base_keys - curr_keys
                    
                    if added:
                        differences.append(f"Fields added at {path}: {', '.join(added)}")
                    if removed:
                        differences.append(f"Fields removed at {path}: {', '.join(removed)}")
                    
                    for key in base_keys & curr_keys:
                        compare_schemas(base[key], curr[key], f"{path}.{key}" if path else key)
            
            compare_schemas(baseline_schema, current_schema)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "drift_detected": len(differences) > 0,
                    "differences": differences,
                    "baseline_schema": baseline_schema,
                    "current_schema": current_schema
                }, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }, indent=2)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
        )]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
