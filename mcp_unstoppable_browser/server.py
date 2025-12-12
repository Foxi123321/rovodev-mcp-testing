#!/usr/bin/env python3
"""
Rex Unstoppable Browser MCP Server
Unrestricted web browsing with anti-detection and Cloudflare bypass
"""

import asyncio
import json
import os
import base64
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

try:
    from mcp.server import Server, NotificationOptions
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    import mcp.server.stdio
    from mcp.server.models import InitializationOptions
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not available")

from patchright.async_api import async_playwright
import requests

# Initialize server
app = Server("rex-unstoppable-browser")

# Global browser instances
_playwright = None
_browser = None
_contexts = {}  # Session management

async def get_browser():
    """Get or create browser instance"""
    global _playwright, _browser
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
    return _browser

async def get_context(session_id: str = "default"):
    """Get or create browser context (session)"""
    if session_id not in _contexts:
        browser = await get_browser()
        _contexts[session_id] = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    return _contexts[session_id]

async def close_context(session_id: str):
    """Close a browser context"""
    if session_id in _contexts:
        await _contexts[session_id].close()
        del _contexts[session_id]
        return True
    return False

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available browser tools"""
    return [
        Tool(
            name="browse_url",
            description="Browse to any URL and get the page content. Bypasses most detection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to browse"},
                    "session_id": {"type": "string", "description": "Session ID for persistent browsing", "default": "default"},
                    "wait_for": {"type": "string", "description": "CSS selector to wait for before returning", "default": None},
                    "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="browse_interact",
            description="Interact with a page: click, fill forms, navigate",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID", "default": "default"},
                    "actions": {
                        "type": "array",
                        "description": "List of actions to perform",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["click", "fill", "goto", "wait", "scroll"]},
                                "selector": {"type": "string", "description": "CSS selector (for click/fill)"},
                                "value": {"type": "string", "description": "Value to fill or URL to goto"},
                                "timeout": {"type": "number", "default": 5000}
                            }
                        }
                    }
                },
                "required": ["actions"]
            }
        ),
        Tool(
            name="browse_screenshot",
            description="Take a screenshot of the current page or a specific element",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "default": "default"},
                    "selector": {"type": "string", "description": "CSS selector to screenshot (or full page if omitted)"},
                    "full_page": {"type": "boolean", "default": False}
                },
                "required": []
            }
        ),
        Tool(
            name="browse_execute_js",
            description="Execute JavaScript code on the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "default": "default"},
                    "script": {"type": "string", "description": "JavaScript code to execute"}
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="extract_data",
            description="Extract data from the current page using CSS selectors",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "default": "default"},
                    "selectors": {
                        "type": "object",
                        "description": "Key-value pairs of field names and CSS selectors",
                        "additionalProperties": {"type": "string"}
                    },
                    "extract_all": {"type": "boolean", "description": "Extract all matches or just first", "default": False}
                },
                "required": ["selectors"]
            }
        ),
        Tool(
            name="bypass_cloudflare",
            description="Use FlareSolverr to bypass Cloudflare protection (nuclear option)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL protected by Cloudflare"},
                    "max_timeout": {"type": "number", "default": 60000}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="session_create",
            description="Create a new browsing session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Unique session identifier"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="session_destroy",
            description="Destroy a browsing session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID to destroy"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="get_cookies",
            description="Get all cookies from current session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "default": "default"}
                },
                "required": []
            }
        ),
        Tool(
            name="set_cookies",
            description="Set cookies for a session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "default": "default"},
                    "cookies": {"type": "array", "description": "Array of cookie objects"}
                },
                "required": ["cookies"]
            }
        )
    ]

@app.call_tool()
async def call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    
    try:
        if name == "browse_url":
            url = arguments["url"]
            session_id = arguments.get("session_id", "default")
            wait_for = arguments.get("wait_for")
            timeout = arguments.get("timeout", 30) * 1000
            
            context = await get_context(session_id)
            page = context.pages[0] if context.pages else await context.new_page()
            
            await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout)
            
            content = await page.content()
            title = await page.title()
            url_final = page.url
            
            result = f"Title: {title}\nURL: {url_final}\n\n{content[:5000]}"
            if len(content) > 5000:
                result += f"\n\n... (truncated, total length: {len(content)} chars)"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "browse_interact":
            session_id = arguments.get("session_id", "default")
            actions = arguments["actions"]
            
            context = await get_context(session_id)
            page = context.pages[0] if context.pages else await context.new_page()
            
            results = []
            for action in actions:
                action_type = action["type"]
                
                if action_type == "goto":
                    await page.goto(action["value"], wait_until="domcontentloaded")
                    results.append(f"Navigated to {action['value']}")
                
                elif action_type == "click":
                    await page.click(action["selector"], timeout=action.get("timeout", 5000))
                    results.append(f"Clicked {action['selector']}")
                
                elif action_type == "fill":
                    await page.fill(action["selector"], action["value"], timeout=action.get("timeout", 5000))
                    results.append(f"Filled {action['selector']} with {action['value']}")
                
                elif action_type == "wait":
                    await page.wait_for_timeout(action.get("value", 1000))
                    results.append(f"Waited {action.get('value', 1000)}ms")
                
                elif action_type == "scroll":
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    results.append("Scrolled to bottom")
            
            return [TextContent(type="text", text="\n".join(results))]
        
        elif name == "browse_screenshot":
            session_id = arguments.get("session_id", "default")
            selector = arguments.get("selector")
            full_page = arguments.get("full_page", False)
            
            context = await get_context(session_id)
            page = context.pages[0] if context.pages else await context.new_page()
            
            if selector:
                element = await page.query_selector(selector)
                screenshot_bytes = await element.screenshot()
            else:
                screenshot_bytes = await page.screenshot(full_page=full_page)
            
            # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"screenshot_{timestamp}.png"
            screenshot_path.write_bytes(screenshot_bytes)
            
            return [
                TextContent(type="text", text=f"Screenshot saved to {screenshot_path}"),
                ImageContent(type="image", data=base64.b64encode(screenshot_bytes).decode(), mimeType="image/png")
            ]
        
        elif name == "browse_execute_js":
            session_id = arguments.get("session_id", "default")
            script = arguments["script"]
            
            context = await get_context(session_id)
            page = context.pages[0] if context.pages else await context.new_page()
            
            result = await page.evaluate(script)
            return [TextContent(type="text", text=f"Result: {json.dumps(result, indent=2)}")]
        
        elif name == "extract_data":
            session_id = arguments.get("session_id", "default")
            selectors = arguments["selectors"]
            extract_all = arguments.get("extract_all", False)
            
            context = await get_context(session_id)
            page = context.pages[0] if context.pages else await context.new_page()
            
            extracted = {}
            for field, selector in selectors.items():
                if extract_all:
                    elements = await page.query_selector_all(selector)
                    extracted[field] = [await el.inner_text() for el in elements]
                else:
                    element = await page.query_selector(selector)
                    extracted[field] = await element.inner_text() if element else None
            
            return [TextContent(type="text", text=json.dumps(extracted, indent=2))]
        
        elif name == "bypass_cloudflare":
            url = arguments["url"]
            max_timeout = arguments.get("max_timeout", 60000)
            
            # Use FlareSolverr approach with selenium/undetected-chromedriver
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Import undetected chromedriver if available
            try:
                import undetected_chromedriver as uc
                options = uc.ChromeOptions()
                options.add_argument('--headless')
                driver = uc.Chrome(options=options)
            except ImportError:
                options = Options()
                options.add_argument('--headless')
                driver = webdriver.Chrome(options=options)
            
            try:
                driver.get(url)
                # Wait for cloudflare to resolve
                WebDriverWait(driver, max_timeout/1000).until(
                    lambda d: "cloudflare" not in d.page_source.lower() or "cf-browser" not in d.page_source.lower()
                )
                
                content = driver.page_source
                cookies = driver.get_cookies()
                
                driver.quit()
                
                result = f"Successfully bypassed Cloudflare!\n\nCookies: {json.dumps(cookies, indent=2)}\n\nContent (first 3000 chars):\n{content[:3000]}"
                return [TextContent(type="text", text=result)]
            except Exception as e:
                driver.quit()
                raise e
        
        elif name == "session_create":
            session_id = arguments["session_id"]
            await get_context(session_id)
            return [TextContent(type="text", text=f"Session '{session_id}' created")]
        
        elif name == "session_destroy":
            session_id = arguments["session_id"]
            if await close_context(session_id):
                return [TextContent(type="text", text=f"Session '{session_id}' destroyed")]
            else:
                return [TextContent(type="text", text=f"Session '{session_id}' not found")]
        
        elif name == "get_cookies":
            session_id = arguments.get("session_id", "default")
            context = await get_context(session_id)
            cookies = await context.cookies()
            return [TextContent(type="text", text=json.dumps(cookies, indent=2))]
        
        elif name == "set_cookies":
            session_id = arguments.get("session_id", "default")
            cookies = arguments["cookies"]
            context = await get_context(session_id)
            await context.add_cookies(cookies)
            return [TextContent(type="text", text=f"Set {len(cookies)} cookies")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rex-unstoppable-browser",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
