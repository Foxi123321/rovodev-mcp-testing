"""Knowledge Database MCP Server - The Heart"""
import asyncio
import logging
from typing import Any, Optional
import json

from mcp.server import Server
from mcp.types import Tool, TextContent

# RovoDev MCP friendly - absolute imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
from search import KnowledgeSearchEngine
from curator import AIDatabaseCurator
from models import (
    CodeFile, CodeKnowledge, CommandPattern, 
    ErrorSolution, SystemMetric
)
from config import DB_PATH, LOG_LEVEL, LOG_FILE

# Setup logging - only to file, not stdout (MCP protocol requires clean stdout)
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

# Initialize server
app = Server("knowledge-db")
db = KnowledgeDatabase(DB_PATH)
search_engine = KnowledgeSearchEngine(db)
curator = AIDatabaseCurator(db)

# Ollama for Gemma queries
import requests
OLLAMA_URL = "http://localhost:11434/api/generate"
GEMMA_MODEL = "gemma2:9b"

def call_gemma(prompt: str, max_tokens: int = 600) -> str:
    """Call Gemma AI through Ollama"""
    try:
        payload = {
            "model": GEMMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": max_tokens
            }
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error calling Gemma: {str(e)}"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        Tool(
            name="query_code_knowledge",
            description="Query code intelligence database for functions, classes, and their purposes",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (function name, purpose, code snippet)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_command_patterns",
            description="Get execution patterns and baseline behavior for a command",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to query (e.g., 'gradle build')"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="store_code_analysis",
            description="Store code analysis results in the knowledge database",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    },
                    "symbols": {
                        "type": "array",
                        "description": "Array of code symbols (functions, classes, etc.)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "purpose": {"type": "string"},
                                "line_start": {"type": "number"},
                                "line_end": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["file_path", "symbols"]
            }
        ),
        Tool(
            name="store_command_result",
            description="Store command execution result and update baselines",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command that was executed"
                    },
                    "duration_ms": {
                        "type": "number",
                        "description": "Execution duration in milliseconds"
                    },
                    "success": {
                        "type": "boolean",
                        "description": "Whether command succeeded"
                    },
                    "exit_code": {
                        "type": "number",
                        "description": "Exit code"
                    },
                    "cpu_avg": {
                        "type": "number",
                        "description": "Average CPU usage %"
                    },
                    "memory_peak_mb": {
                        "type": "number",
                        "description": "Peak memory usage in MB"
                    },
                    "output_snippet": {
                        "type": "string",
                        "description": "Output snippet (first/last lines)"
                    }
                },
                "required": ["command", "duration_ms", "success"]
            }
        ),
        Tool(
            name="get_error_solution",
            description="Find known solutions for an error pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "error_pattern": {
                        "type": "string",
                        "description": "Error message or pattern to search for"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context (command, environment, etc.)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of solutions",
                        "default": 5
                    }
                },
                "required": ["error_pattern"]
            }
        ),
        Tool(
            name="store_solution",
            description="Store a new error solution or update existing one",
            inputSchema={
                "type": "object",
                "properties": {
                    "error_pattern": {
                        "type": "string",
                        "description": "Error pattern"
                    },
                    "solution": {
                        "type": "string",
                        "description": "Solution description"
                    },
                    "success": {
                        "type": "boolean",
                        "description": "Whether solution worked"
                    },
                    "context": {
                        "type": "string",
                        "description": "When this solution applies"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source: manual, web_research, ai_generated"
                    }
                },
                "required": ["error_pattern", "solution", "success"]
            }
        ),
        Tool(
            name="get_system_baseline",
            description="Get system baseline metrics for this machine",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_knowledge",
            description="Search across all knowledge types (code, commands, errors)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Max results per category",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="run_database_curator",
            description="Run AI-powered database curation (cleanup, optimization, insights)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "Specific tasks to run: duplicates, archiving, confidence, anomalies, tagging, relationships, insights. Empty = run all",
                        "items": {"type": "string"}
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="ask_gemma",
            description="Ask Gemma AI (the librarian) a question about the codebase. Gemma reads the Knowledge DB and provides intelligent answers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question to ask Gemma about the codebase"
                    },
                    "context_limit": {
                        "type": "number",
                        "description": "Number of relevant code entries to include as context",
                        "default": 20
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="get_database_health",
            description="Get current database health metrics and quality score",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_curator_insights",
            description="Get AI-generated insights about database contents and patterns",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")
        
        if name == "query_code_knowledge":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            results = db.query_code_knowledge(query, limit)
            return [TextContent(
                type="text",
                text=json.dumps(results, indent=2, default=str)
            )]
        
        elif name == "query_command_patterns":
            command = arguments["command"]
            baseline = db.get_command_baseline(command)
            
            if baseline:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "baseline": baseline,
                        "message": f"Found baseline for '{command}'"
                    }, indent=2, default=str)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "baseline": None,
                        "message": f"No baseline found for '{command}'. This command hasn't been executed yet."
                    }, indent=2)
                )]
        
        elif name == "store_code_analysis":
            file_path = arguments["file_path"]
            project_name = arguments.get("project_name")
            language = arguments.get("language")
            symbols = arguments["symbols"]
            
            # Store file
            code_file = CodeFile(
                file_path=file_path,
                project_name=project_name,
                language=language
            )
            file_id = db.store_code_file(code_file)
            
            # Store symbols
            stored_count = 0
            for symbol in symbols:
                knowledge = CodeKnowledge(
                    file_id=file_id,
                    symbol_name=symbol["name"],
                    symbol_type=symbol["type"],
                    purpose=symbol.get("purpose"),
                    line_start=symbol.get("line_start"),
                    line_end=symbol.get("line_end")
                )
                db.store_code_knowledge(knowledge)
                stored_count += 1
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "file_id": file_id,
                    "symbols_stored": stored_count,
                    "message": f"Stored {stored_count} symbols from {file_path}"
                }, indent=2)
            )]
        
        elif name == "store_command_result":
            pattern = CommandPattern(
                command=arguments["command"],
                duration_ms=arguments["duration_ms"],
                success=arguments["success"],
                exit_code=arguments.get("exit_code"),
                cpu_avg=arguments.get("cpu_avg"),
                memory_peak_mb=arguments.get("memory_peak_mb"),
                output_snippet=arguments.get("output_snippet")
            )
            
            pattern_id = db.store_command_pattern(pattern)
            baseline = db.get_command_baseline(pattern.command)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "pattern_id": pattern_id,
                    "baseline_updated": baseline,
                    "message": f"Stored execution result and updated baseline for '{pattern.command}'"
                }, indent=2, default=str)
            )]
        
        elif name == "get_error_solution":
            error_pattern = arguments["error_pattern"]
            context = arguments.get("context")
            limit = arguments.get("limit", 5)
            
            if context:
                solutions = search_engine.suggest_solutions(error_pattern, context)
            else:
                solutions = db.get_error_solution(error_pattern, limit)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "solutions": solutions,
                    "count": len(solutions),
                    "message": f"Found {len(solutions)} potential solution(s)"
                }, indent=2, default=str)
            )]
        
        elif name == "store_solution":
            solution = ErrorSolution(
                error_pattern=arguments["error_pattern"],
                solution=arguments["solution"],
                context=arguments.get("context"),
                source=arguments.get("source", "manual"),
                success_count=1 if arguments["success"] else 0,
                failure_count=0 if arguments["success"] else 1,
                confidence=1.0 if arguments["success"] else 0.0
            )
            
            solution_id = db.store_error_solution(solution)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "solution_id": solution_id,
                    "message": f"Stored solution for error pattern"
                }, indent=2)
            )]
        
        elif name == "get_system_baseline":
            baseline = db.get_system_baseline()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "baseline": baseline,
                    "message": "System baseline metrics"
                }, indent=2, default=str)
            )]
        
        elif name == "search_knowledge":
            query = arguments["query"]
            limit = arguments.get("limit", 20)
            
            results = search_engine.search(query, limit=limit)
            
            total_results = sum(len(v) for v in results.values())
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "results": results,
                    "total_results": total_results,
                    "message": f"Found {total_results} total results"
                }, indent=2, default=str)
            )]
        
        elif name == "run_database_curator":
            tasks = arguments.get("tasks", [])
            
            logger.info(f"Running database curator with tasks: {tasks or 'all'}")
            
            # Run full curation
            results = await curator.run_full_curation()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "results": results,
                    "message": "Database curation completed"
                }, indent=2, default=str)
            )]
        
        elif name == "get_database_health":
            health = await curator.get_database_health()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "health": health,
                    "message": f"Database health: {health['status']}"
                }, indent=2, default=str)
            )]
        
        elif name == "get_curator_insights":
            insights = await curator.generate_insights()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "insights": insights,
                    "message": "AI-generated insights"
                }, indent=2, default=str)
            )]
        
        elif name == "ask_gemma":
            question = arguments["question"]
            context_limit = arguments.get("context_limit", 20)
            
            # Get relevant code entries for context
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT ck.symbol_name, ck.purpose, cf.file_path
                FROM code_knowledge ck
                JOIN code_files cf ON ck.file_id = cf.id
                LIMIT ?
            """, (context_limit,))
            
            context_entries = cursor.fetchall()
            context_text = "\n".join([
                f"- {row['symbol_name']}: {row['purpose'][:100]}..."
                for row in context_entries
            ])
            
            # Build prompt for Gemma
            prompt = f"""You are analyzing a codebase with knowledge from the database.

Sample code entries:
{context_text}

User question: {question}

Provide a clear, concise answer based on the code knowledge available."""
            
            # Call Gemma
            answer = call_gemma(prompt, max_tokens=800)
            
            return [TextContent(
                type="text",
                text=answer
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
                "error": str(e),
                "tool": name
            })
        )]


async def main():
    """Run the server"""
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting Knowledge Database MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
