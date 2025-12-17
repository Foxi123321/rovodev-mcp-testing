"""Filesystem/Artifacts MCP Server - Secure artifact management and storage.

This server provides safe, organized access to execution artifacts:
- Screenshots from browser tests
- Logs from executions
- Test results and reports
- Files created during execution
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from tools.artifact_manager import ArtifactManager


# Initialize server
app = Server("filesystem-artifacts")

# Initialize artifact manager with secure paths
base_path = Path(__file__).parent / "artifacts"
artifact_manager = ArtifactManager(base_path=base_path)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available filesystem/artifact tools."""
    return [
        Tool(
            name="store_artifact",
            description="Store an artifact (screenshot, log, test result, etc.) with metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_type": {
                        "type": "string",
                        "description": "Type of artifact",
                        "enum": ["screenshot", "log", "test_result", "report", "file", "other"]
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to store"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadata (test name, timestamp, tags, etc.)",
                        "properties": {
                            "test_name": {"type": "string"},
                            "execution_id": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "description": {"type": "string"}
                        }
                    }
                },
                "required": ["artifact_type", "file_path"]
            }
        ),
        Tool(
            name="retrieve_artifact",
            description="Retrieve an artifact by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Unique artifact ID"
                    }
                },
                "required": ["artifact_id"]
            }
        ),
        Tool(
            name="list_artifacts",
            description="List all artifacts, optionally filtered",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_type": {
                        "type": "string",
                        "description": "Filter by type"
                    },
                    "execution_id": {
                        "type": "string",
                        "description": "Filter by execution ID"
                    },
                    "tags": {
                        "type": "array",
                        "description": "Filter by tags",
                        "items": {"type": "string"}
                    }
                }
            }
        ),
        Tool(
            name="create_artifact_bundle",
            description="Bundle multiple artifacts together (e.g., all artifacts from a test run)",
            inputSchema={
                "type": "object",
                "properties": {
                    "bundle_name": {
                        "type": "string",
                        "description": "Name for the bundle"
                    },
                    "artifact_ids": {
                        "type": "array",
                        "description": "List of artifact IDs to include",
                        "items": {"type": "string"}
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Bundle metadata"
                    }
                },
                "required": ["bundle_name", "artifact_ids"]
            }
        ),
        Tool(
            name="get_artifact_stats",
            description="Get statistics about stored artifacts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cleanup_old_artifacts",
            description="Remove artifacts older than specified days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_old": {
                        "type": "integer",
                        "description": "Remove artifacts older than this many days"
                    },
                    "artifact_type": {
                        "type": "string",
                        "description": "Only clean specific type (optional)"
                    }
                },
                "required": ["days_old"]
            }
        ),
        Tool(
            name="read_file_safe",
            description="Safely read a file from allowed paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file (must be in allowed paths)"
                    },
                    "max_size_kb": {
                        "type": "integer",
                        "description": "Maximum file size to read (default: 1024 KB)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="list_directory_safe",
            description="List contents of a directory (only allowed paths)",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to list"
                    }
                },
                "required": ["directory"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI assistants."""
    
    try:
        if name == "store_artifact":
            result = await artifact_manager.store_artifact(
                artifact_type=arguments["artifact_type"],
                file_path=arguments["file_path"],
                metadata=arguments.get("metadata", {})
            )
        
        elif name == "retrieve_artifact":
            result = await artifact_manager.retrieve_artifact(
                artifact_id=arguments["artifact_id"]
            )
        
        elif name == "list_artifacts":
            result = await artifact_manager.list_artifacts(
                artifact_type=arguments.get("artifact_type"),
                execution_id=arguments.get("execution_id"),
                tags=arguments.get("tags")
            )
        
        elif name == "create_artifact_bundle":
            result = await artifact_manager.create_bundle(
                bundle_name=arguments["bundle_name"],
                artifact_ids=arguments["artifact_ids"],
                metadata=arguments.get("metadata", {})
            )
        
        elif name == "get_artifact_stats":
            result = await artifact_manager.get_stats()
        
        elif name == "cleanup_old_artifacts":
            result = await artifact_manager.cleanup_old_artifacts(
                days_old=arguments["days_old"],
                artifact_type=arguments.get("artifact_type")
            )
        
        elif name == "read_file_safe":
            result = await artifact_manager.read_file_safe(
                file_path=arguments["file_path"],
                max_size_kb=arguments.get("max_size_kb", 1024)
            )
        
        elif name == "list_directory_safe":
            result = await artifact_manager.list_directory_safe(
                directory=arguments["directory"]
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
