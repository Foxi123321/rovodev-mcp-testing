"""Failure-Classifier MCP Server - Classifies failures and decides recovery strategy.

This server analyzes failures and determines:
- Execution Error (retry same step)
- Plan Gap (partial replan)
- Missing Capability (blocker - stop)
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from tools.failure_classifier import FailureClassifier


# Initialize server
app = Server("failure-classifier")

# Initialize classifier with local AI
classifier = FailureClassifier(
    model_name=os.getenv("CLASSIFIER_MODEL", "gemma2:9b"),
    ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available failure classification tools."""
    return [
        Tool(
            name="classify_failure",
            description="Classify a failure into: EXECUTION_ERROR, PLAN_GAP, or MISSING_CAPABILITY. Returns recovery strategy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "failure_description": {
                        "type": "string",
                        "description": "What failed and how"
                    },
                    "audit_results": {
                        "type": "object",
                        "description": "Results from execution-auditor (which steps failed/blocked)"
                    },
                    "original_plan": {
                        "type": "string",
                        "description": "The original approved plan"
                    },
                    "error_logs": {
                        "type": "string",
                        "description": "Optional: Error logs/stack traces"
                    }
                },
                "required": ["failure_description", "audit_results", "original_plan"]
            }
        ),
        Tool(
            name="suggest_recovery_action",
            description="Get specific recovery action based on failure classification",
            inputSchema={
                "type": "object",
                "properties": {
                    "failure_type": {
                        "type": "string",
                        "description": "EXECUTION_ERROR, PLAN_GAP, or MISSING_CAPABILITY",
                        "enum": ["EXECUTION_ERROR", "PLAN_GAP", "MISSING_CAPABILITY"]
                    },
                    "failure_context": {
                        "type": "object",
                        "description": "Context about the failure"
                    }
                },
                "required": ["failure_type", "failure_context"]
            }
        ),
        Tool(
            name="should_retry",
            description="Determine if a failed step should be retried (and how many times)",
            inputSchema={
                "type": "object",
                "properties": {
                    "failure_description": {
                        "type": "string",
                        "description": "What failed"
                    },
                    "retry_count": {
                        "type": "integer",
                        "description": "How many times this has been retried already"
                    },
                    "error_pattern": {
                        "type": "string",
                        "description": "Pattern of the error (transient, deterministic, etc.)"
                    }
                },
                "required": ["failure_description", "retry_count"]
            }
        ),
        Tool(
            name="identify_root_cause",
            description="Analyze failure to identify root cause (not just symptoms)",
            inputSchema={
                "type": "object",
                "properties": {
                    "failure_chain": {
                        "type": "array",
                        "description": "Sequence of events leading to failure",
                        "items": {"type": "string"}
                    },
                    "error_logs": {
                        "type": "string",
                        "description": "Error logs/stack traces"
                    }
                },
                "required": ["failure_chain"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI assistants."""
    
    try:
        if name == "classify_failure":
            result = await classifier.classify_failure(
                failure_description=arguments["failure_description"],
                audit_results=arguments["audit_results"],
                original_plan=arguments["original_plan"],
                error_logs=arguments.get("error_logs", "")
            )
        
        elif name == "suggest_recovery_action":
            result = await classifier.suggest_recovery_action(
                failure_type=arguments["failure_type"],
                failure_context=arguments["failure_context"]
            )
        
        elif name == "should_retry":
            result = await classifier.should_retry(
                failure_description=arguments["failure_description"],
                retry_count=arguments["retry_count"],
                error_pattern=arguments.get("error_pattern", "")
            )
        
        elif name == "identify_root_cause":
            result = await classifier.identify_root_cause(
                failure_chain=arguments["failure_chain"],
                error_logs=arguments.get("error_logs", "")
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
