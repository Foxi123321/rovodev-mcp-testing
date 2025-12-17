"""
Index the TEST directory and analyze it
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server import handle_index_codebase, handle_query_codebase, handle_analyze_function, handle_get_stats
from database_manager import DatabaseManager

async def main():
    print("=" * 80)
    print("INDEXING TEST CODEBASE")
    print("=" * 80)
    print()
    
    test_path = r"C:\Users\ggfuc\.rovodev\mcp_deep_learning_v2\TEST"
    
    # Index the codebase
    print("[1/4] Indexing codebase...")
    result = await handle_index_codebase({
        "path": test_path,
        "recursive": True
    })
    print(result)
    print()
    
    # Get stats
    print("[2/4] Getting system stats...")
    stats_result = await handle_get_stats({})
    print(stats_result)
    print()
    
    # Analyze a specific function
    print("[3/4] Analyzing 'login' function...")
    analysis = await handle_analyze_function({
        "function_name": "login"
    })
    print(analysis)
    print()
    
    # Query the codebase
    print("[4/4] Testing query: 'What handles user authentication?'")
    query_result = await handle_query_codebase({
        "question": "What handles user authentication?",
        "top_k": 3
    })
    print(query_result)
    print()
    
    print("=" * 80)
    print("INDEXING COMPLETE - AIs NOW KNOW EVERYTHING!")
    print("=" * 80)
    
    # Show what was learned
    db = DatabaseManager()
    entities = db.search_entities()
    
    print(f"\nTotal entities indexed: {len(entities)}")
    print("\nFunctions found:")
    for entity in entities:
        if entity['entity_type'] == 'function':
            print(f"  - {entity['name']} (in {entity['file_path'].split('TEST')[-1]})")
    
    print("\nClasses found:")
    for entity in entities:
        if entity['entity_type'] == 'class':
            print(f"  - {entity['name']} (in {entity['file_path'].split('TEST')[-1]})")

if __name__ == "__main__":
    asyncio.run(main())
