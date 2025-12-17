"""
Analyze EVERY function/class in the TEST codebase
Both AIs (DeepSeek + Qwen) will learn the complete code
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database_manager import DatabaseManager
from server import handle_analyze_function
import time

async def main():
    print("=" * 80)
    print("COMPLETE CODEBASE ANALYSIS - MAKING AIs LEARN EVERYTHING")
    print("=" * 80)
    print()
    
    db = DatabaseManager()
    
    # Get all entities
    entities = db.search_entities()
    
    print(f"Found {len(entities)} entities to analyze\n")
    print("This will take a while - both DeepSeek and Qwen will analyze each one...\n")
    
    analyzed_count = 0
    start_time = time.time()
    
    for idx, entity in enumerate(entities, 1):
        fname = entity['file_path'].split('\\')[-1]
        print(f"[{idx}/{len(entities)}] Analyzing {entity['entity_type']}: {entity['name']} (in {fname})")
        print("-" * 80)
        
        try:
            result = await handle_analyze_function({
                "function_name": entity['name'],
                "file_path": fname
            })
            
            # Show a snippet of the analysis
            if "Analysis:" in result:
                lines = result.split('\n')
                # Show first 10 lines of analysis
                preview = '\n'.join(lines[:15])
                print(preview)
                if len(lines) > 15:
                    print("...(truncated)")
            else:
                print(result[:200])
            
            analyzed_count += 1
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        print()
        
        # Show progress
        elapsed = time.time() - start_time
        avg_time = elapsed / analyzed_count if analyzed_count > 0 else 0
        remaining = (len(entities) - analyzed_count) * avg_time
        print(f"Progress: {analyzed_count}/{len(entities)} | Elapsed: {elapsed:.1f}s | Est. remaining: {remaining:.1f}s")
        print()
    
    print("=" * 80)
    print("COMPLETE ANALYSIS FINISHED!")
    print("=" * 80)
    
    # Final stats
    stats = db.get_stats()
    print(f"\nDatabase Stats:")
    print(f"  - Files indexed: {stats['files']}")
    print(f"  - Code entities: {stats['entities']}")
    print(f"  - Analyses performed: {stats['analyses']}")
    print(f"  - Total time: {time.time() - start_time:.1f}s")
    print()
    print("✓ Both AIs now know EVERYTHING about the TEST codebase!")
    print("✓ You can now ask me (Rex) about ANY function and I'll know it!")

if __name__ == "__main__":
    asyncio.run(main())
