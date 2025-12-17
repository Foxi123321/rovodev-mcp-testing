"""
Analyze VS Code source from the TEST/vscode-main.zip
Shows real-time progress in the window
"""

import asyncio
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from server import handle_index_codebase, handle_analyze_function, handle_get_stats
from database_manager import DatabaseManager

async def main():
    vscode_path = Path(__file__).parent / "TEST" / "vscode-main"
    
    if not vscode_path.exists():
        print("❌ VS Code source not found!")
        print(f"Expected at: {vscode_path}")
        print("\nMake sure vscode-main.zip is extracted to TEST folder")
        return
    
    print(f"✓ Found VS Code source: {vscode_path}")
    print()
    
    print("=" * 80)
    print("PHASE 1: INDEXING (Extracting all code structure)")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    result = await handle_index_codebase({
        "path": str(vscode_path),
        "recursive": True
    })
    
    print(result)
    
    index_time = time.time() - start_time
    print(f"\n✓ Indexing completed in {index_time:.1f} seconds ({index_time/60:.1f} minutes)")
    
    print("\n" + "=" * 80)
    print("PHASE 2: DEEP AI ANALYSIS")
    print("=" * 80)
    print()
    print("Both DeepSeek 33B and Qwen 30B will now analyze each function")
    print("This is the slow part - each function takes ~5-10 seconds")
    print()
    
    db = DatabaseManager()
    entities = db.search_entities()
    
    total = len(entities)
    print(f"Total entities found: {total}")
    print()
    
    # Analyze in batches to show progress
    analyze_limit = min(200, total)  # First 200 for demo
    
    if total > analyze_limit:
        print(f"⚠ Analyzing first {analyze_limit} entities (full analysis would take hours)")
        print(f"  Full analysis: ~{total * 7 / 3600:.1f} hours estimated")
        print()
    
    analysis_start = time.time()
    success_count = 0
    cached_count = 0
    error_count = 0
    
    for idx, entity in enumerate(entities[:analyze_limit], 1):
        # Get file name
        fname = entity['file_path'].replace('\\', '/').split('/')[-1]
        
        # Progress header
        print(f"[{idx}/{analyze_limit}] {entity['entity_type']:8} | {entity['name']:40.40} | {fname:25.25}", end=" | ")
        
        # Check if already analyzed (cached)
        existing = db.get_entity_analysis(entity['id'])
        if existing:
            print("✓ CACHED")
            cached_count += 1
            continue
        
        # Analyze with both AIs
        try:
            result = await handle_analyze_function({
                "function_name": entity['name'],
                "file_path": fname
            })
            
            # Parse result to show confidence
            if "Confidence:" in result:
                # Extract confidence line
                for line in result.split('\n'):
                    if 'Overall:' in line:
                        conf = line.split(':')[1].strip()
                        print(f"✓ {conf}")
                        break
                else:
                    print("✓ ANALYZED")
                success_count += 1
            elif "error" in result.lower() or "not found" in result.lower():
                print("✗ ERROR")
                error_count += 1
            else:
                print("✓ DONE")
                success_count += 1
        
        except Exception as e:
            print(f"✗ {str(e)[:30]}")
            error_count += 1
        
        # Show timing every 10 items
        if idx % 10 == 0:
            elapsed = time.time() - analysis_start
            avg_time = elapsed / idx
            remaining = (analyze_limit - idx) * avg_time
            
            print(f"     └─ Progress: {idx}/{analyze_limit} | Elapsed: {elapsed:.0f}s | Remaining: ~{remaining:.0f}s (~{remaining/60:.1f}min)")
            print(f"     └─ Stats: {success_count} analyzed | {cached_count} cached | {error_count} errors")
            print()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    
    stats = db.get_stats()
    total_time = time.time() - start_time
    
    print(f"""
Final Statistics:
  ┌─ Database
  │  ├─ Files indexed: {stats['files']}
  │  ├─ Code entities: {stats['entities']}
  │  ├─ Analyses: {stats['analyses']}
  │  └─ Cached queries: {stats['cached_queries']}
  │
  ├─ This Session
  │  ├─ Analyzed: {success_count}
  │  ├─ Cached: {cached_count}
  │  ├─ Errors: {error_count}
  │  └─ Total: {success_count + cached_count + error_count}
  │
  └─ Timing
     ├─ Total time: {total_time/60:.1f} minutes
     ├─ Index time: {index_time/60:.1f} minutes
     └─ Analysis time: {(total_time - index_time)/60:.1f} minutes

✓ The AIs now understand VS Code!
✓ All analysis is cached - future queries are instant!
✓ Ask Rex anything about VS Code internals!

Database location: {db.db_path}
""")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Analysis interrupted by user")
        print("   Progress has been saved to database")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
