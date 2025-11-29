"""MCP Testing & Review Server - Code review and browser automation for AI assistants."""
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from tools.code_reviewer import CodeReviewer
from tools.browser_tester import BrowserTester
from tools.app_tester import AppTester
from tools.image_analyzer import ImageAnalyzer


# Load config
config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    CONFIG = json.load(f)

# Initialize server
app = Server("testing-review-server")

# Initialize tools
code_reviewer = CodeReviewer()
browser_tester = BrowserTester(CONFIG)
app_tester = AppTester()
image_analyzer = ImageAnalyzer()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available testing and review tools."""
    return [
        # Code Review Tools
        Tool(
            name="review_code",
            description="Review a code file for security issues, bugs, and code smells",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to review"
                    }
                },
                "required": ["file_path"]
            }
        ),
        
        # Browser Automation Tools
        Tool(
            name="browser_navigate",
            description="Navigate browser to a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="browser_click",
            description="Click an element on the page by CSS selector",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector of the element to click"
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="browser_fill",
            description="Fill an input field with text",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector of the input field"
                    },
                    "value": {
                        "type": "string",
                        "description": "Text to fill into the field"
                    }
                },
                "required": ["selector", "value"]
            }
        ),
        Tool(
            name="browser_screenshot",
            description="Capture a screenshot of the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Optional name for the screenshot file"
                    }
                }
            }
        ),
        Tool(
            name="browser_get_errors",
            description="Get console errors and warnings from the page",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="browser_execute_js",
            description="Execute JavaScript code in the browser context",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "JavaScript code to execute"
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="browser_close",
            description="Close the browser",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # Image Analysis Tools
        Tool(
            name="analyze_screenshot",
            description="Analyze a screenshot using vision AI to detect UI issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the screenshot image"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Optional custom analysis prompt"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="detect_ui_issues",
            description="Check screenshot for common UI/UX problems",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the screenshot image"
                    }
                },
                "required": ["image_path"]
            }
        ),
        
        # Desktop App Testing Tools
        Tool(
            name="launch_desktop_app",
            description="Launch a desktop application",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to launch the app (e.g., 'python app.py')"
                    },
                    "wait_time": {
                        "type": "integer",
                        "description": "Seconds to wait for app to start (default: 3)"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="click_screen",
            description="Click at specific screen coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="send_keystrokes",
            description="Type text or press keys",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="press_key",
            description="Press a single key (enter, space, tab, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to press"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="screenshot_desktop",
            description="Capture desktop screenshot",
            inputSchema={
                "type": "object",
                "properties": {
                    "save_path": {
                        "type": "string",
                        "description": "Path to save screenshot"
                    }
                },
                "required": ["save_path"]
            }
        ),
        Tool(
            name="get_mouse_position",
            description="Get current mouse cursor position",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="close_desktop_app",
            description="Close the launched desktop application",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI assistants."""
    
    try:
        # Code Review Tools
        if name == "review_code":
            result = code_reviewer.review_file(arguments["file_path"])
        
        # Browser Tools
        elif name == "browser_navigate":
            result = await browser_tester.navigate(arguments["url"])
        
        elif name == "browser_click":
            result = await browser_tester.click_element(arguments["selector"])
        
        elif name == "browser_fill":
            result = await browser_tester.fill_input(
                arguments["selector"],
                arguments["value"]
            )
        
        elif name == "browser_screenshot":
            result = await browser_tester.get_screenshot(
                arguments.get("name")
            )
        
        elif name == "browser_get_errors":
            result = await browser_tester.get_console_errors()
        
        elif name == "browser_execute_js":
            result = await browser_tester.evaluate_js(arguments["script"])
        
        elif name == "browser_close":
            result = await browser_tester.close()
        
        # Image Analysis Tools
        elif name == "analyze_screenshot":
            result = image_analyzer.analyze_screenshot(
                arguments["image_path"],
                arguments.get("prompt")
            )
        
        elif name == "detect_ui_issues":
            result = image_analyzer.detect_ui_issues(arguments["image_path"])
        
        # Desktop App Testing Tools
        elif name == "launch_desktop_app":
            result = app_tester.launch_app(
                arguments["command"],
                arguments.get("wait_time", 3)
            )
        
        elif name == "click_screen":
            result = app_tester.click_at(arguments["x"], arguments["y"])
        
        elif name == "send_keystrokes":
            result = app_tester.send_keys(arguments["text"])
        
        elif name == "press_key":
            result = app_tester.press_key(arguments["key"])
        
        elif name == "screenshot_desktop":
            result = app_tester.take_screenshot(save_path=arguments["save_path"])
        
        elif name == "get_mouse_position":
            result = app_tester.get_mouse_position()
        
        elif name == "close_desktop_app":
            result = app_tester.close_app()
        
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
