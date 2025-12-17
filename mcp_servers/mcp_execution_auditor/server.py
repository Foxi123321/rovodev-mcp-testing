"""Execution-Auditor MCP Server - Verifies execution against approved plans.

This server compares what was PLANNED vs what was actually EXECUTED.
It prevents declaring success without evidence.
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from tools.execution_auditor import ExecutionAuditor


# Initialize server
app = Server("execution-auditor")

# Initialize auditor with local AI
auditor = ExecutionAuditor(
    model_name=os.getenv("AUDITOR_MODEL", "qwen3-coder:30b"),
    ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available execution auditing tools."""
    return [
        Tool(
            name="audit_execution",
            description="Compare planned steps vs executed steps. Returns status for each step: DONE, FAILED, or BLOCKED.",
            inputSchema={
                "type": "object",
                "properties": {
                    "approved_plan": {
                        "type": "string",
                        "description": "The original approved plan (from Plan-Validator)"
                    },
                    "execution_summary": {
                        "type": "string",
                        "description": "Summary of what was actually executed"
                    },
                    "artifacts": {
                        "type": "object",
                        "description": "Evidence artifacts (test results, logs, screenshots, files created, etc.)",
                        "properties": {
                            "files_created": {"type": "array", "items": {"type": "string"}},
                            "tests_run": {"type": "array", "items": {"type": "object"}},
                            "screenshots": {"type": "array", "items": {"type": "string"}},
                            "logs": {"type": "string"},
                            "other": {"type": "object"}
                        }
                    }
                },
                "required": ["approved_plan", "execution_summary"]
            }
        ),
        Tool(
            name="verify_definition_of_done",
            description="Check if the Definition of Done criteria were actually met",
            inputSchema={
                "type": "object",
                "properties": {
                    "definition_of_done": {
                        "type": "string",
                        "description": "The DoD criteria from the plan"
                    },
                    "artifacts": {
                        "type": "object",
                        "description": "Evidence artifacts"
                    }
                },
                "required": ["definition_of_done", "artifacts"]
            }
        ),
        Tool(
            name="compare_plan_vs_execution",
            description="Step-by-step comparison of plan vs execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_steps": {
                        "type": "array",
                        "description": "List of planned steps",
                        "items": {"type": "string"}
                    },
                    "executed_steps": {
                        "type": "array",
                        "description": "List of what was actually done",
                        "items": {"type": "string"}
                    }
                },
                "required": ["plan_steps", "executed_steps"]
            }
        ),
        Tool(
            name="check_evidence_quality",
            description="Assess if provided evidence is sufficient to prove completion",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "What is being claimed as done"
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Evidence provided"
                    }
                },
                "required": ["claim", "evidence"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI assistants."""
    
    try:
        if name == "audit_execution":
            result = await auditor.audit_execution(
                approved_plan=arguments["approved_plan"],
                execution_summary=arguments["execution_summary"],
                artifacts=arguments.get("artifacts", {})
            )
        
        elif name == "verify_definition_of_done":
            result = await auditor.verify_definition_of_done(
                definition_of_done=arguments["definition_of_done"],
                artifacts=arguments["artifacts"]
            )
        
        elif name == "compare_plan_vs_execution":
            result = await auditor.compare_plan_vs_execution(
                plan_steps=arguments["plan_steps"],
                executed_steps=arguments["executed_steps"]
            )
        
        elif name == "check_evidence_quality":
            result = await auditor.check_evidence_quality(
                claim=arguments["claim"],
                evidence=arguments["evidence"]
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
