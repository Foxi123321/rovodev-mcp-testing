#!/usr/bin/env python3
"""
Deployment/Container MCP Server
Provides Docker and container management operations
"""

import json
import subprocess
from typing import Any
import asyncio

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp")
    exit(1)

app = Server("deployment")

def run_docker_command(args: list[str]) -> dict:
    """Execute docker command"""
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "Docker not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available deployment tools"""
    return [
        Tool(
            name="docker_ps",
            description="List running containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Show all containers (not just running)"
                    }
                }
            }
        ),
        Tool(
            name="docker_build",
            description="Build a Docker image",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to build context"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Image tag"
                    },
                    "dockerfile": {
                        "type": "string",
                        "description": "Dockerfile name (optional)"
                    }
                },
                "required": ["path", "tag"]
            }
        ),
        Tool(
            name="docker_run",
            description="Run a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Image name"
                    },
                    "name": {
                        "type": "string",
                        "description": "Container name"
                    },
                    "ports": {
                        "type": "object",
                        "description": "Port mappings (e.g., {'8080': '80'})"
                    },
                    "env": {
                        "type": "object",
                        "description": "Environment variables"
                    },
                    "detach": {
                        "type": "boolean",
                        "description": "Run in background"
                    }
                },
                "required": ["image"]
            }
        ),
        Tool(
            name="docker_stop",
            description="Stop a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    }
                },
                "required": ["container"]
            }
        ),
        Tool(
            name="docker_logs",
            description="Get container logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to show"
                    }
                },
                "required": ["container"]
            }
        ),
        Tool(
            name="docker_compose_up",
            description="Start services with docker-compose",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "docker-compose.yml path"
                    },
                    "detach": {
                        "type": "boolean",
                        "description": "Run in background"
                    }
                },
                "required": ["file"]
            }
        ),
        Tool(
            name="docker_compose_down",
            description="Stop services with docker-compose",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "docker-compose.yml path"
                    }
                },
                "required": ["file"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "docker_ps":
            show_all = arguments.get("all", False)
            cmd = ["ps"]
            if show_all:
                cmd.append("-a")
            
            result = run_docker_command(cmd)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "containers": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
                }, indent=2)
            )]
        
        elif name == "docker_build":
            path = arguments["path"]
            tag = arguments["tag"]
            dockerfile = arguments.get("dockerfile")
            
            cmd = ["build", "-t", tag, path]
            if dockerfile:
                cmd.extend(["-f", dockerfile])
            
            result = run_docker_command(cmd)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
                }, indent=2)
            )]
        
        elif name == "docker_run":
            image = arguments["image"]
            container_name = arguments.get("name")
            ports = arguments.get("ports", {})
            env = arguments.get("env", {})
            detach = arguments.get("detach", True)
            
            cmd = ["run"]
            if detach:
                cmd.append("-d")
            if container_name:
                cmd.extend(["--name", container_name])
            
            for host_port, container_port in ports.items():
                cmd.extend(["-p", f"{host_port}:{container_port}"])
            
            for key, value in env.items():
                cmd.extend(["-e", f"{key}={value}"])
            
            cmd.append(image)
            
            result = run_docker_command(cmd)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "container_id": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
                }, indent=2)
            )]
        
        elif name == "docker_stop":
            container = arguments["container"]
            
            result = run_docker_command(["stop", container])
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
                }, indent=2)
            )]
        
        elif name == "docker_logs":
            container = arguments["container"]
            tail = arguments.get("tail")
            
            cmd = ["logs", container]
            if tail:
                cmd.extend(["--tail", str(tail)])
            
            result = run_docker_command(cmd)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "logs": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
                }, indent=2)
            )]
        
        elif name == "docker_compose_up":
            compose_file = arguments["file"]
            detach = arguments.get("detach", True)
            
            cmd = ["compose", "-f", compose_file, "up"]
            if detach:
                cmd.append("-d")
            
            result = run_docker_command(cmd)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
                }, indent=2)
            )]
        
        elif name == "docker_compose_down":
            compose_file = arguments["file"]
            
            result = run_docker_command(["compose", "-f", compose_file, "down"])
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") or result.get("error")
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
