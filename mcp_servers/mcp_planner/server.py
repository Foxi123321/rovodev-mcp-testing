#!/usr/bin/env python3
"""
Planner MCP Server
Provides intelligent task decomposition and planning using Ollama
"""

import json
import subprocess
from typing import Any, Optional
import asyncio

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("ERROR: MCP SDK not installed")
    exit(1)

app = Server("planner")

def call_ollama(model: str, prompt: str, system: str = "") -> dict:
    """Call Ollama API"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True
            # timeout removed - no limit for complex reasoning tasks
        )
        
        if result.returncode != 0:
            return {"success": False, "error": "Ollama request failed"}
        
        response = json.loads(result.stdout)
        
        return {
            "success": True,
            "response": response.get("response", ""),
            "model": response.get("model", model)
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available planner tools"""
    return [
        Tool(
            name="decompose_task",
            description="Break down a complex task into smaller actionable steps",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task to decompose"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context about the task"
                    },
                    "model": {
                        "type": "string",
                        "description": "Ollama model to use (default: qwen3-coder:30b)",
                        "default": "qwen3-coder:30b"
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="create_implementation_plan",
            description="Create a detailed implementation plan with dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "The implementation goal"
                    },
                    "constraints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Constraints or requirements"
                    },
                    "model": {
                        "type": "string",
                        "description": "Ollama model to use",
                        "default": "qwen3-coder:30b"
                    }
                },
                "required": ["goal"]
            }
        ),
        Tool(
            name="estimate_task_complexity",
            description="Estimate complexity and effort for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task to estimate"
                    },
                    "model": {
                        "type": "string",
                        "description": "Ollama model to use",
                        "default": "gemma2:9b"
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="identify_dependencies",
            description="Identify task dependencies and execution order",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tasks to analyze"
                    },
                    "model": {
                        "type": "string",
                        "description": "Ollama model to use",
                        "default": "qwen3-coder:30b"
                    }
                },
                "required": ["tasks"]
            }
        ),
        Tool(
            name="suggest_optimizations",
            description="Suggest optimizations for a plan or approach",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The plan to optimize"
                    },
                    "model": {
                        "type": "string",
                        "description": "Ollama model to use",
                        "default": "gemma2:9b"
                    }
                },
                "required": ["plan"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "decompose_task":
            task = arguments["task"]
            context = arguments.get("context", "")
            model = arguments.get("model", "qwen3-coder:30b")
            
            system_prompt = """You are a task planning expert. Break down complex tasks into clear, actionable steps.
Output as JSON array with this structure:
[
  {"step": 1, "action": "description", "dependencies": []},
  {"step": 2, "action": "description", "dependencies": [1]}
]"""
            
            prompt = f"Task: {task}\n"
            if context:
                prompt += f"Context: {context}\n"
            prompt += "\nBreak this into clear steps. Output JSON only."
            
            result = call_ollama(model, prompt, system_prompt)
            
            if not result["success"]:
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": result["error"]}, indent=2)
                )]
            
            # Try to parse JSON from response
            response_text = result["response"]
            try:
                # Extract JSON if wrapped in text
                if "[" in response_text and "]" in response_text:
                    start = response_text.index("[")
                    end = response_text.rindex("]") + 1
                    steps = json.loads(response_text[start:end])
                else:
                    steps = response_text
            except:
                steps = response_text
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "task": task,
                    "steps": steps,
                    "model": model
                }, indent=2)
            )]
        
        elif name == "create_implementation_plan":
            goal = arguments["goal"]
            constraints = arguments.get("constraints", [])
            model = arguments.get("model", "qwen3-coder:30b")
            
            system_prompt = "You are a software architect. Create detailed implementation plans."
            
            prompt = f"Goal: {goal}\n"
            if constraints:
                prompt += f"Constraints: {', '.join(constraints)}\n"
            prompt += "\nCreate a detailed implementation plan with phases, tasks, and dependencies."
            
            result = call_ollama(model, prompt, system_prompt)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "goal": goal,
                    "plan": result.get("response", ""),
                    "error": result.get("error")
                }, indent=2)
            )]
        
        elif name == "estimate_task_complexity":
            task = arguments["task"]
            model = arguments.get("model", "gemma2:9b")
            
            system_prompt = """Estimate task complexity. Output JSON:
{
  "complexity": "low|medium|high",
  "effort_hours": number,
  "risks": ["risk1", "risk2"],
  "reasoning": "explanation"
}"""
            
            prompt = f"Task: {task}\n\nEstimate complexity. Output JSON only."
            
            result = call_ollama(model, prompt, system_prompt)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "task": task,
                    "estimate": result.get("response", ""),
                    "error": result.get("error")
                }, indent=2)
            )]
        
        elif name == "identify_dependencies":
            tasks = arguments["tasks"]
            model = arguments.get("model", "qwen3-coder:30b")
            
            system_prompt = "Analyze task dependencies and determine optimal execution order."
            
            prompt = f"Tasks:\n"
            for i, t in enumerate(tasks, 1):
                prompt += f"{i}. {t}\n"
            prompt += "\nIdentify dependencies and suggest execution order."
            
            result = call_ollama(model, prompt, system_prompt)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "tasks": tasks,
                    "analysis": result.get("response", ""),
                    "error": result.get("error")
                }, indent=2)
            )]
        
        elif name == "suggest_optimizations":
            plan = arguments["plan"]
            model = arguments.get("model", "gemma2:9b")
            
            system_prompt = "You are an optimization expert. Suggest improvements to plans and approaches."
            
            prompt = f"Plan:\n{plan}\n\nSuggest optimizations and improvements."
            
            result = call_ollama(model, prompt, system_prompt)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "original_plan": plan,
                    "suggestions": result.get("response", ""),
                    "error": result.get("error")
                }, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}, indent=2)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
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

