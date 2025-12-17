#!/usr/bin/env python3
"""
GitOps MCP Server
Provides local git operations for development workflow automation
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional
import asyncio

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("ERROR: MCP SDK not installed. Run: pip install mcp")
    exit(1)

app = Server("gitops")

def run_git_command(args: list[str], cwd: str = ".") -> dict:
    """Execute git command and return result"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Git command timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitOps tools"""
    return [
        Tool(
            name="git_status",
            description="Get git repository status",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)"
                    }
                }
            }
        ),
        Tool(
            name="git_diff",
            description="Show git diff for changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Specific file to diff (optional)"
                    },
                    "staged": {
                        "type": "boolean",
                        "description": "Show staged changes only"
                    }
                }
            }
        ),
        Tool(
            name="git_commit",
            description="Create a git commit",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    },
                    "add_all": {
                        "type": "boolean",
                        "description": "Stage all changes before committing"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="git_branch",
            description="List, create, or switch branches",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "switch", "delete"],
                        "description": "Branch action to perform"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Branch name (required for create/switch/delete)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="git_log",
            description="Show git commit history",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of commits to show (default: 10)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Show history for specific file"
                    }
                }
            }
        ),
        Tool(
            name="git_add",
            description="Stage files for commit",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to stage (use ['.'] for all)"
                    }
                },
                "required": ["files"]
            }
        ),
        Tool(
            name="git_reset",
            description="Unstage or reset changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to reset (optional, resets all if empty)"
                    },
                    "hard": {
                        "type": "boolean",
                        "description": "Hard reset (WARNING: discards changes)"
                    }
                }
            }
        ),
        Tool(
            name="git_stash",
            description="Stash or restore changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["save", "pop", "list", "apply"],
                        "description": "Stash action"
                    },
                    "message": {
                        "type": "string",
                        "description": "Stash message (for save action)"
                    }
                },
                "required": ["action"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        repo_path = arguments.get("repo_path", ".")
        
        if name == "git_status":
            result = run_git_command(["status", "--short", "--branch"], repo_path)
            
            if result["success"]:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "status": result["stdout"]
                    }, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": result.get("stderr") or result.get("error")
                    }, indent=2)
                )]
        
        elif name == "git_diff":
            file_path = arguments.get("file_path")
            staged = arguments.get("staged", False)
            
            cmd = ["diff"]
            if staged:
                cmd.append("--staged")
            if file_path:
                cmd.append(file_path)
            
            result = run_git_command(cmd, repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "diff": result["stdout"],
                    "error": result.get("stderr") if not result["success"] else None
                }, indent=2)
            )]
        
        elif name == "git_commit":
            message = arguments["message"]
            add_all = arguments.get("add_all", False)
            
            if add_all:
                add_result = run_git_command(["add", "-A"], repo_path)
                if not add_result["success"]:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"Failed to stage changes: {add_result.get('stderr')}"
                        }, indent=2)
                    )]
            
            result = run_git_command(["commit", "-m", message], repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "message": result["stdout"],
                    "error": result.get("stderr") if not result["success"] else None
                }, indent=2)
            )]
        
        elif name == "git_branch":
            action = arguments["action"]
            branch_name = arguments.get("branch_name")
            
            if action == "list":
                result = run_git_command(["branch", "-a"], repo_path)
            elif action == "create":
                if not branch_name:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"success": False, "error": "branch_name required"}, indent=2)
                    )]
                result = run_git_command(["branch", branch_name], repo_path)
            elif action == "switch":
                if not branch_name:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"success": False, "error": "branch_name required"}, indent=2)
                    )]
                result = run_git_command(["checkout", branch_name], repo_path)
            elif action == "delete":
                if not branch_name:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"success": False, "error": "branch_name required"}, indent=2)
                    )]
                result = run_git_command(["branch", "-d", branch_name], repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") if not result["success"] else None
                }, indent=2)
            )]
        
        elif name == "git_log":
            limit = arguments.get("limit", 10)
            file_path = arguments.get("file_path")
            
            cmd = ["log", f"-{limit}", "--oneline", "--decorate"]
            if file_path:
                cmd.append(file_path)
            
            result = run_git_command(cmd, repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "commits": result["stdout"].split("\n") if result["stdout"] else [],
                    "error": result.get("stderr") if not result["success"] else None
                }, indent=2)
            )]
        
        elif name == "git_add":
            files = arguments["files"]
            
            result = run_git_command(["add"] + files, repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "message": f"Staged {len(files)} file(s)",
                    "error": result.get("stderr") if not result["success"] else None
                }, indent=2)
            )]
        
        elif name == "git_reset":
            files = arguments.get("files", [])
            hard = arguments.get("hard", False)
            
            cmd = ["reset"]
            if hard:
                cmd.append("--hard")
            cmd.extend(files)
            
            result = run_git_command(cmd, repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") if not result["success"] else None
                }, indent=2)
            )]
        
        elif name == "git_stash":
            action = arguments["action"]
            message = arguments.get("message", "")
            
            if action == "save":
                cmd = ["stash", "push"]
                if message:
                    cmd.extend(["-m", message])
            elif action == "pop":
                cmd = ["stash", "pop"]
            elif action == "list":
                cmd = ["stash", "list"]
            elif action == "apply":
                cmd = ["stash", "apply"]
            
            result = run_git_command(cmd, repo_path)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result["success"],
                    "output": result["stdout"],
                    "error": result.get("stderr") if not result["success"] else None
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
