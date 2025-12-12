#!/usr/bin/env python3
"""
Simple Vision MCP Server - Uses PowerShell script for reliable execution
"""
import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any
from datetime import datetime

from mcp.server import Server, NotificationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio
from mcp.server.models import InitializationOptions

app = Server("vision-server-simple")

SCRIPT_PATH = Path(__file__).parent / "analyze_image_async.ps1"

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available vision tools."""
    return [
        Tool(
            name="analyze_image",
            description="Analyze an image using vision AI (llava). Returns immediately with file path to result.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "What to analyze about the image",
                        "default": "Describe this image in detail"
                    },
                    "wait": {
                        "type": "boolean",
                        "description": "If true, wait for result. If false, return immediately with output file path.",
                        "default": False
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="read_analysis",
            description="Read a completed vision analysis result from file",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_file": {
                        "type": "string",
                        "description": "Path to the analysis output file"
                    }
                },
                "required": ["output_file"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "analyze_image":
            image_path = arguments["image_path"]
            prompt = arguments.get("prompt", "Describe this image in detail")
            wait = arguments.get("wait", False)
            
            if not Path(image_path).exists():
                return [TextContent(
                    type="text",
                    text=f"Error: Image not found: {image_path}"
                )]
            
            # Generate output filename
            job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(__file__).parent / "screenshots" / f"analysis_{job_id}.txt"
            output_file.parent.mkdir(exist_ok=True)
            
            if wait:
                # Run synchronously and wait
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT_PATH),
                     "-ImagePath", image_path, "-Prompt", prompt, "-OutputFile", str(output_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if output_file.exists():
                    analysis = output_file.read_text(encoding='utf-8')
                    return [TextContent(
                        type="text",
                        text=f"Analysis complete!\n\n{analysis}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Error: Analysis failed\n{result.stderr}"
                    )]
            else:
                # Start in background and return immediately
                subprocess.Popen(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT_PATH),
                     "-ImagePath", image_path, "-Prompt", prompt, "-OutputFile", str(output_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                return [TextContent(
                    type="text",
                    text=f"✅ Analysis started in background!\n\n"
                         f"📁 Output file: {output_file}\n"
                         f"⏱️  Wait ~15 seconds, then use read_analysis tool\n\n"
                         f"Or read directly:\nGet-Content '{output_file}'"
                )]
        
        elif name == "read_analysis":
            output_file = Path(arguments["output_file"])
            
            if not output_file.exists():
                return [TextContent(
                    type="text",
                    text=f"File not found (analysis may still be running): {output_file}"
                )]
            
            content = output_file.read_text(encoding='utf-8')
            return [TextContent(
                type="text",
                text=f"Analysis Result:\n\n{content}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vision-server-simple",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
