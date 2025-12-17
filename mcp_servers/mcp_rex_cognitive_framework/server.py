"""Rex Cognitive Framework MCP Server.

Provides cognitive intelligence tools for website understanding and exploration.
"""

import asyncio
import json
import sys
import os
from typing import Any

# Add the workspace path to import the framework
WORKSPACE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "OneDrive", "Desktop", "Rexs whishes")
sys.path.insert(0, WORKSPACE_PATH)

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    import mcp.types as types
except ImportError:
    print("ERROR: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from tools.cognitive_tools import (
    explore_website,
    analyze_website_state,
    create_exploration_goal,
    validate_website_schema,
    pivot_strategy,
    store_knowledge,
    retrieve_knowledge,
    run_integration_test
)

# Create server instance
server = Server("rex-cognitive-framework")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available cognitive framework tools."""
    return [
        types.Tool(
            name="explore_website",
            description="Execute full cognitive exploration loop on a website (OBSERVE→DECIDE→ACT→LEARN)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL to explore"
                    },
                    "goal_type": {
                        "type": "string",
                        "enum": ["discovery", "data_extraction", "interaction", "validation"],
                        "description": "Type of exploration goal"
                    },
                    "target_description": {
                        "type": "string",
                        "description": "What you're looking for or trying to accomplish"
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "Maximum exploration iterations (default: 10)",
                        "default": 10
                    }
                },
                "required": ["url", "goal_type", "target_description"]
            }
        ),
        types.Tool(
            name="analyze_website_state",
            description="Analyze a website's current state and structure with confidence scoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL to analyze"
                    },
                    "include_vision": {
                        "type": "boolean",
                        "description": "Use vision AI for analysis (default: false)",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="create_exploration_goal",
            description="Create a structured exploration goal for the cognitive framework",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal_type": {
                        "type": "string",
                        "enum": ["discovery", "data_extraction", "interaction", "validation"],
                        "description": "Type of exploration goal"
                    },
                    "target_description": {
                        "type": "string",
                        "description": "What you're trying to accomplish"
                    },
                    "constraints": {
                        "type": "object",
                        "description": "Optional constraints (time, resources, etc)",
                        "default": {}
                    }
                },
                "required": ["goal_type", "target_description"]
            }
        ),
        types.Tool(
            name="validate_website_schema",
            description="Validate a website state against the mental model schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "Website state object to validate"
                    }
                },
                "required": ["state"]
            }
        ),
        types.Tool(
            name="pivot_strategy",
            description="Intelligently switch between UI and API strategies based on website state",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL"
                    },
                    "current_state": {
                        "type": "object",
                        "description": "Current website state"
                    },
                    "goal": {
                        "type": "object",
                        "description": "Exploration goal"
                    }
                },
                "required": ["url", "current_state", "goal"]
            }
        ),
        types.Tool(
            name="store_knowledge",
            description="Store learned patterns and website state in persistent knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL"
                    },
                    "state": {
                        "type": "object",
                        "description": "Website state to store"
                    },
                    "patterns": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Learned patterns",
                        "default": []
                    }
                },
                "required": ["url", "state"]
            }
        ),
        types.Tool(
            name="retrieve_knowledge",
            description="Retrieve previously learned website state and patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL to retrieve knowledge for"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="run_integration_test",
            description="Run full integration test across all 5 phases of the cognitive framework",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "enum": ["ecommerce", "news", "api"],
                        "description": "Test scenario to run",
                        "default": "all"
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    
    if arguments is None:
        arguments = {}
    
    try:
        if name == "explore_website":
            result = await explore_website(
                arguments["url"],
                arguments["goal_type"],
                arguments["target_description"],
                arguments.get("max_iterations", 10)
            )
            
        elif name == "analyze_website_state":
            result = await analyze_website_state(
                arguments["url"],
                arguments.get("include_vision", False)
            )
            
        elif name == "create_exploration_goal":
            result = create_exploration_goal(
                arguments["goal_type"],
                arguments["target_description"],
                arguments.get("constraints", {})
            )
            
        elif name == "validate_website_schema":
            result = validate_website_schema(arguments["state"])
            
        elif name == "pivot_strategy":
            result = await pivot_strategy(
                arguments["url"],
                arguments["current_state"],
                arguments["goal"]
            )
            
        elif name == "store_knowledge":
            result = await store_knowledge(
                arguments["url"],
                arguments["state"],
                arguments.get("patterns", [])
            )
            
        elif name == "retrieve_knowledge":
            result = await retrieve_knowledge(arguments["url"])
            
        elif name == "run_integration_test":
            result = await run_integration_test(
                arguments.get("scenario", "all")
            )
            
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [types.TextContent(type="text", text=json.dumps({"error": error_msg}, indent=2))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rex-cognitive-framework",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
