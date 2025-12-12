"""
Deep Learning Intelligence MCP Server v2
Provides code analysis tools for Rex using dual-AI system
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Local imports
from config import (
    TECHNICAL_ANALYSIS_PROMPT,
    SEMANTIC_ANALYSIS_PROMPT,
    DATA_DIR,
    LOG_LEVEL
)
from ollama_client import OllamaClient
from database_manager import DatabaseManager
from code_parser import CodeParser
from vector_store import VectorStore, CodeEmbedder
from consensus_engine import ConsensusEngine
from knowledge_db_bridge import get_bridge

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
db = DatabaseManager()
parser = CodeParser()
vector_store = VectorStore()
knowledge_bridge = get_bridge()  # Bridge to shared Knowledge DB

# MCP Server
app = Server("deep-learning-intelligence-v2")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for Rex to use"""
    return [
        Tool(
            name="index_codebase",
            description="Index a codebase for analysis. Parses all files, extracts functions/classes, stores in database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the codebase directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Recursively index subdirectories",
                        "default": True
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="analyze_function",
            description="Deep analysis of a specific function using both DeepSeek and Qwen. Returns technical and semantic understanding with consensus.",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function to analyze"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional: specific file path to narrow search"
                    }
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="analyze_code",
            description="Analyze any code snippet using dual-AI system. Provides technical implementation details and semantic purpose.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code snippet to analyze"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about the code (what file it's from, what it's used for, etc.)"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, typescript, etc.)"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="query_codebase",
            description="Ask questions about the indexed codebase. Uses semantic search to find relevant code and provides intelligent answers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question about the codebase (e.g., 'what handles authentication?', 'find all database queries')"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of relevant code snippets to consider",
                        "default": 5
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="get_dependencies",
            description="Get dependencies for a function or class. Shows what it calls and what calls it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                        "description": "Name of function or class"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["from", "to", "both"],
                        "description": "Direction of dependencies to retrieve",
                        "default": "both"
                    }
                },
                "required": ["entity_name"]
            }
        ),
        Tool(
            name="find_similar_code",
            description="Find code similar to a given snippet using vector search. Great for finding duplicates or related functionality.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code snippet to find similar matches for"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of similar results to return",
                        "default": 5
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="get_system_stats",
            description="Get statistics about the indexed codebase and analysis system.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls from Rex"""
    
    try:
        if name == "index_codebase":
            result = await handle_index_codebase(arguments)
        
        elif name == "analyze_function":
            result = await handle_analyze_function(arguments)
        
        elif name == "analyze_code":
            result = await handle_analyze_code(arguments)
        
        elif name == "query_codebase":
            result = await handle_query_codebase(arguments)
        
        elif name == "get_dependencies":
            result = await handle_get_dependencies(arguments)
        
        elif name == "find_similar_code":
            result = await handle_find_similar_code(arguments)
        
        elif name == "get_system_stats":
            result = await handle_get_stats(arguments)
        
        else:
            result = f"Unknown tool: {name}"
        
        return [TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_index_codebase(args: Dict[str, Any]) -> str:
    """Index a codebase"""
    path = Path(args["path"])
    recursive = args.get("recursive", True)
    
    if not path.exists():
        return f"Error: Path not found: {path}"
    
    logger.info(f"Indexing codebase at {path}")
    
    # Parse directory
    parsed_files = parser.parse_directory(path, recursive=recursive)
    
    if not parsed_files:
        return f"No supported files found in {path}"
    
    # Store in database
    total_entities = 0
    async with OllamaClient() as client:
        embedder = CodeEmbedder(client)
        
        for file_data in parsed_files:
            # Store file
            file_id = db.store_file(
                file_data["file_path"],
                file_data["language"],
                file_data["size_bytes"],
                file_data["last_modified"],
                file_data["content_hash"]
            )
            
            # Store entities and create embeddings
            for entity in file_data["entities"]:
                entity_id = db.store_entity(
                    file_id,
                    entity["entity_type"],
                    entity["name"],
                    entity.get("signature"),
                    entity.get("start_line"),
                    entity.get("end_line"),
                    entity.get("code_snippet")
                )
                
                # Create embedding for vector search
                embedding = await embedder.embed_code(
                    entity["code_snippet"],
                    context=f"File: {file_data['file_path']}\nType: {entity['entity_type']}\nName: {entity['name']}"
                )
                
                if embedding:
                    await vector_store.add_embedding(
                        embedding,
                        {
                            "entity_id": entity_id,
                            "name": entity["name"],
                            "type": entity["entity_type"],
                            "file": file_data["file_path"],
                            "line": entity.get("start_line")
                        }
                    )
                
                total_entities += 1
    
    # Save vector index
    vector_store.save()
    
    stats = db.get_stats()
    return f"""✓ Indexed codebase successfully!

Files indexed: {len(parsed_files)}
Functions/Classes found: {total_entities}
Total entities in DB: {stats['entities']}
Vector embeddings created: {vector_store.get_stats()['total_vectors']}

Ready for analysis!"""


async def handle_analyze_function(args: Dict[str, Any]) -> str:
    """Analyze a specific function"""
    function_name = args["function_name"]
    file_path = args.get("file_path")
    
    # Search for function in database
    entities = db.search_entities(name=function_name, file_path=file_path)
    
    if not entities:
        return f"Function '{function_name}' not found in indexed codebase."
    
    if len(entities) > 1 and not file_path:
        # Multiple matches
        matches = "\n".join([f"  - {e['file_path']}:{e['start_line']}" for e in entities[:5]])
        return f"Multiple matches found for '{function_name}':\n{matches}\n\nSpecify file_path to narrow down."
    
    # Use first match
    entity = entities[0]
    
    # Check if already analyzed
    existing_analysis = db.get_entity_analysis(entity["id"])
    if existing_analysis:
        return format_analysis_result(entity, existing_analysis)
    
    # Perform dual-AI analysis
    async with OllamaClient() as client:
        result = await client.analyze_code_dual(
            code=entity["code_snippet"],
            context=f"File: {entity['file_path']}\nFunction: {entity['name']}\nLine: {entity['start_line']}",
            technical_prompt=TECHNICAL_ANALYSIS_PROMPT,
            semantic_prompt=SEMANTIC_ANALYSIS_PROMPT
        )
        
        # Create consensus
        consensus = ConsensusEngine.merge_analyses(
            result["primary"],
            result["secondary"]
        )
        
        # Store in database
        analysis_data = {
            "analysis_type": "function_analysis",
            "primary_model": result["primary"]["model"],
            "primary_summary": result["primary"]["response"],
            "primary_details": {},
            "primary_confidence": 0.8 if result["primary"]["success"] else 0.0,
            "secondary_model": result["secondary"]["model"] if result["secondary"] else None,
            "secondary_summary": result["secondary"]["response"] if result["secondary"] else "",
            "secondary_details": {},
            "secondary_confidence": 0.8 if result["secondary"] and result["secondary"]["success"] else 0.0,
            "consensus_summary": consensus["consensus_summary"],
            "consensus_confidence": consensus["consensus_confidence"],
            "agreement_score": consensus["agreement_score"],
            "needs_review": consensus["needs_review"]
        }
        
        db.store_analysis(entity["id"], analysis_data)
        
        # Sync to shared Knowledge DB
        knowledge_bridge.sync_analysis(entity, analysis_data)
        
        return format_analysis_result(entity, analysis_data)


async def handle_analyze_code(args: Dict[str, Any]) -> str:
    """Analyze arbitrary code snippet"""
    code = args["code"]
    context = args.get("context", "")
    language = args.get("language", "")
    
    async with OllamaClient() as client:
        result = await client.analyze_code_dual(
            code=code,
            context=f"Language: {language}\n{context}",
            technical_prompt=TECHNICAL_ANALYSIS_PROMPT,
            semantic_prompt=SEMANTIC_ANALYSIS_PROMPT
        )
        
        consensus = ConsensusEngine.merge_analyses(
            result["primary"],
            result["secondary"]
        )
        
        quality = ConsensusEngine.analyze_result_quality(consensus)
        
        output = f"""=== Code Analysis ===

{consensus['consensus_summary']}

--- Analysis Quality ---
Confidence: {consensus['consensus_confidence']:.0%}
Agreement: {consensus['agreement_score']:.0%}
Quality Level: {quality['quality_level']}
Recommendation: {quality['recommendation']}
"""
        
        if consensus['needs_review']:
            output += "\n⚠️ AI models disagreed - human review recommended"
        
        return output


async def handle_query_codebase(args: Dict[str, Any]) -> str:
    """Query the codebase with natural language"""
    question = args["question"]
    top_k = args.get("top_k", 5)
    
    # Check cache first
    cached = db.get_cached_query(question)
    if cached:
        return cached
    
    # Create embedding for question
    async with OllamaClient() as client:
        embedder = CodeEmbedder(client)
        question_embedding = await embedder.embed_code(question)
        
        if not question_embedding:
            return "Error: Could not create embedding for question"
        
        # Search vector store
        similar_code = await vector_store.search(question_embedding, top_k=top_k)
        
        if not similar_code:
            return f"No relevant code found for: {question}"
        
        # Get entities and their analysis
        context_parts = []
        for result in similar_code:
            entity_id = result["entity_id"]
            entity = db.search_entities(name=result["name"])[0] if db.search_entities(name=result["name"]) else None
            
            if entity:
                analysis = db.get_entity_analysis(entity_id)
                summary = analysis["consensus_summary"][:200] if analysis else "Not analyzed yet"
                
                context_parts.append(f"""
**{result['name']}** ({result['type']}) - Similarity: {result['similarity_score']:.0%}
File: {result['file']}:{result.get('line', '?')}
Summary: {summary}
""")
        
        # Ask AI to synthesize answer
        context_text = "\n".join(context_parts)
        prompt = f"""Based on the following code from the codebase, answer this question: {question}

Relevant Code:
{context_text}

Provide a clear, concise answer with specific references to the code."""
        
        response = await client.generate(
            model="deepseek-coder:33b",
            prompt=prompt,
            temperature=0.2
        )
        
        answer = response["response"]
        
        # Cache the result
        db.cache_query(question, answer)
        
        return answer


async def handle_get_dependencies(args: Dict[str, Any]) -> str:
    """Get dependencies for an entity"""
    entity_name = args["entity_name"]
    direction = args.get("direction", "both")
    
    # Find entity
    entities = db.search_entities(name=entity_name)
    
    if not entities:
        return f"Entity '{entity_name}' not found in indexed codebase."
    
    entity = entities[0]
    
    # Get dependencies
    deps = db.get_dependencies(entity["id"], direction=direction)
    
    if not deps:
        return f"No dependencies found for '{entity_name}'"
    
    output = f"=== Dependencies for {entity_name} ===\n\n"
    
    for dep in deps:
        dep_type = dep["dependency_type"]
        if "to_name" in dep:
            output += f"  → {dep_type}: {dep['to_name']} ({dep['to_type']})\n"
        else:
            output += f"  ← {dep_type}: {dep['from_name']} ({dep['from_type']})\n"
    
    return output


async def handle_find_similar_code(args: Dict[str, Any]) -> str:
    """Find similar code using vector search"""
    code = args["code"]
    top_k = args.get("top_k", 5)
    
    async with OllamaClient() as client:
        embedder = CodeEmbedder(client)
        embedding = await embedder.embed_code(code)
        
        if not embedding:
            return "Error: Could not create embedding for code"
        
        results = await vector_store.search(embedding, top_k=top_k)
        
        if not results:
            return "No similar code found"
        
        output = "=== Similar Code ===\n\n"
        
        for result in results:
            output += f"""**{result['name']}** ({result['type']})
File: {result['file']}:{result.get('line', '?')}
Similarity: {result['similarity_score']:.0%}

"""
        
        return output


async def handle_get_stats(args: Dict[str, Any]) -> str:
    """Get system statistics"""
    db_stats = db.get_stats()
    vector_stats = vector_store.get_stats()
    
    return f"""=== Deep Learning Intelligence Stats ===

Database:
  - Files indexed: {db_stats['files']}
  - Code entities: {db_stats['entities']}
  - Analyses performed: {db_stats['analyses']}
  - Dependencies tracked: {db_stats['dependencies']}
  - Cached queries: {db_stats['cached_queries']}

Vector Search:
  - Enabled: {vector_stats['enabled']}
  - Total embeddings: {vector_stats['total_vectors']}
  - Index size: {vector_stats.get('index_size_mb', 0):.2f} MB

Storage Location: {DATA_DIR}
"""


def format_analysis_result(entity: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """Format analysis result for display"""
    output = f"""=== Analysis: {entity['name']} ===

Location: {entity['file_path']}:{entity['start_line']}
Type: {entity['entity_type']}

{analysis['consensus_summary']}

--- Confidence Metrics ---
Overall: {analysis['consensus_confidence']:.0%}
Agreement: {analysis['agreement_score']:.0%}
"""
    
    if analysis['needs_review']:
        output += "\n⚠️ Models disagreed - review recommended"
    
    return output


async def main():
    """Run the MCP server"""
    logger.info("Starting Deep Learning Intelligence MCP Server v2")
    logger.info(f"Data directory: {DATA_DIR}")
    
    # Test Ollama connection
    async with OllamaClient() as client:
        from ollama_client import test_ollama_connection
        await test_ollama_connection()
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
