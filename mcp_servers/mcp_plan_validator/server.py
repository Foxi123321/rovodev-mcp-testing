"""Plan-Validator MCP Server - Validates execution plans before they run.

This server acts as a gatekeeper to prevent incomplete, vague, or unexecutable plans
from being executed. It uses local AI (Qwen/Gemma) to perform strict validation.
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from tools.plan_validator import PlanValidator


# Initialize server
app = Server("plan-validator")

# Initialize validator with local AI
# CHANGED: Use qwen3-coder:30b for MAXIMUM context (you already have it!)
validator = PlanValidator(
    model_name=os.getenv("VALIDATOR_MODEL", "qwen3-coder:30b"),
    ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available plan validation tools."""
    return [
        Tool(
            name="validate_plan",
            description="Validate an execution plan for completeness, feasibility, and verifiability. Returns PASS or FAIL with specific issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The execution plan to validate (markdown or structured text)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional: Additional context about available tools, constraints, or requirements"
                    },
                    "strict_mode": {
                        "type": "boolean",
                        "description": "Enable strict validation (fails on any ambiguity)",
                        "default": True
                    }
                },
                "required": ["plan"]
            }
        ),
        Tool(
            name="validate_plan_from_file",
            description="Validate a large execution plan from a file (for plans >100KB). Useful for massive plans that exceed MCP parameter limits.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the plan file"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional: Additional context about available tools, constraints, or requirements"
                    },
                    "strict_mode": {
                        "type": "boolean",
                        "description": "Enable strict validation (fails on any ambiguity)",
                        "default": True
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="validate_plan_against_mcp_tools",
            description="Validate that a plan only uses tools that are actually available in the MCP ecosystem",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The execution plan to validate"
                    },
                    "available_tools": {
                        "type": "array",
                        "description": "List of available MCP tool names",
                        "items": {"type": "string"}
                    }
                },
                "required": ["plan", "available_tools"]
            }
        ),
        Tool(
            name="check_definition_of_done",
            description="Verify that a plan has clear, measurable success criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The execution plan to check"
                    }
                },
                "required": ["plan"]
            }
        ),
        Tool(
            name="suggest_plan_improvements",
            description="Get suggestions for improving a plan (only call this if validation fails)",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The plan that failed validation"
                    },
                    "validation_errors": {
                        "type": "array",
                        "description": "List of validation errors from validate_plan",
                        "items": {"type": "string"}
                    }
                },
                "required": ["plan", "validation_errors"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI assistants."""
    
    try:
        if name == "validate_plan":
            result = await validator.validate_plan(
                plan=arguments["plan"],
                context=arguments.get("context"),
                strict_mode=arguments.get("strict_mode", True)
            )
        
        elif name == "validate_plan_from_file":
            result = await validator.validate_plan_from_file(
                file_path=arguments["file_path"],
                context=arguments.get("context"),
                strict_mode=arguments.get("strict_mode", True)
            )
        
        elif name == "validate_plan_against_mcp_tools":
            result = await validator.validate_against_available_tools(
                plan=arguments["plan"],
                available_tools=arguments["available_tools"]
            )
        
        elif name == "check_definition_of_done":
            result = await validator.check_definition_of_done(
                plan=arguments["plan"]
            )
        
        elif name == "suggest_plan_improvements":
            result = await validator.suggest_improvements(
                plan=arguments["plan"],
                validation_errors=arguments["validation_errors"]
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
