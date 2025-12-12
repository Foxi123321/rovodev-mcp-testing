"""
Analyze ANY codebase - point it at a directory and watch it learn!
"""

import asyncio
import sys
from pathlib import Path
import time

if len(sys.argv) < 2:
    print("Usage: python analyze_any_code.py <path-to-code>")
    sys.exit(1)

code_path = Path(sys.argv[1])

if not code_path.exists():
    print(f"Error: Path doesn't exist: {code_path}")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))

from server import handle_index_codebase, handle_analyze_function, handle_get_stats
from database_manager import DatabaseManager

async def main():
    print("\n" + "=" * 80)
    print("DEEP LEARNING CODE ANALYSIS")
    print("=" * 80)
    print(f"Target: {code_path}")
    print()
    
    print("STEP 1: INDEXING...")
    print("-" * 80)
    
    start_time = time.time()
    
    result = await handle_index_codebase({
        "path": str(code_path),
        "recursive": True
    })
    
    print(result)
    print(f"\nIndexing time: {time.time() - start_time:.1f}s")
    
    print("\n" + "=" * 80)
    print("STEP 2: AI ANALYSIS (DeepSeek 33B + Qwen 30B)")
    print("=" * 80)
    print()
    
    db = DatabaseManager()
    entities = db.search_entities()
    
    total = len(entities)
    
    if total == 0:
        print("No code entities found!")
        return
    
    # Analyze up to 100 entities (configurable)
    analyze_limit = min(100, total)
    
    print(f"Found {total} entities")
    print(f"Analyzing first {analyze_limit}...")
    print()
    
    analysis_start = time.time()
    analyzed_count = 0
    
    for idx, entity in enumerate(entities[:analyze_limit], 1):
        fname = entity['file_path'].split('\\')[-1].split('/')[-1]
        
        print(f"[{idx}/{analyze_limit}] {entity['entity_type']}: {entity['name']} ({fname})", end=" ... ")
        
        # Check cache
        existing = db.get_entity_analysis(entity['id'])
        if existing:
            print("✓ cached")
            continue
        
        try:
            result = await handle_analyze_function({
                "function_name": entity['name'],
                "file_path": fname
            })
            
            if "Confidence:" in result or "consensus" in result.lower():
                print("✓ analyzed")
                analyzed_count += 1
            else:
                print("⚠ issue")
        
        except Exception as e:
            print(f"✗ error: {e}")
        
        # Progress indicator
        if idx % 10 == 0:
            elapsed = time.time() - analysis_start
            avg = elapsed / idx
            remaining = (analyze_limit - idx) * avg
            print(f"    [{elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining]")
    
    print("\n" + "=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    
    stats = db.get_stats()
    total_time = time.time() - start_time
    
    print(f"""
Results:
  - Files: {stats['files']}
  - Entities: {stats['entities']}
  - Analyses: {stats['analyses']}
  - Time: {total_time/60:.1f} minutes

✓ AIs now understand this codebase!
✓ Ask Rex anything about it!
""")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Stopped by user")
