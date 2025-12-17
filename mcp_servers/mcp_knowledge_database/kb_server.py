"""Knowledge Database MCP Server - Rewritten"""
import asyncio
import logging
from typing import Any, Optional
import json
from pathlib import Path

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Setup logging
LOG_DIR = Path(__file__).parent
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "knowledge_db.log")
    ]
)
logger = logging.getLogger(__name__)

# Local imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
from search import KnowledgeSearchEngine
from curator import AIDatabaseCurator
from config import DB_PATH

# Initialize server
app = Server("knowledge-database")

# Initialize components (lazy)
db = None
search_engine = None
curator = None

def get_db():
    global db, search_engine, curator
    if db is None:
        db = KnowledgeDatabase(DB_PATH)
        search_engine = KnowledgeSearchEngine(db)
        curator = AIDatabaseCurator(db)
    return db, search_engine, curator


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_knowledge",
            description="Search the knowledge database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_conversation_memory",
            description="Query past conversation memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        db_obj, search_obj, curator_obj = get_db()
        
        if name == "search_knowledge":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)
            results = search_obj.search_all(query, limit=limit)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "results": results
                })
            )]
        
        elif name == "query_conversation_memory":
            # Placeholder for now
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Memory querying coming soon"
                })
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown tool: {name}"
                })
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e)
            })
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting Knowledge Database MCP Server (New)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
