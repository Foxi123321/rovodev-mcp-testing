"""Test import order"""
# Try importing MCP BEFORE asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio
print("MCP first, then asyncio works!")
