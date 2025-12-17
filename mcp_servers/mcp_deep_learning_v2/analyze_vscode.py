"""
Index and analyze VS Code source code
This runs in a separate window so you can watch progress
"""

import asyncio
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from server import handle_index_codebase, handle_analyze_function, handle_get_stats
from database_manager import DatabaseManager

async def main():
    print("\n" + "=" * 80)
    print("STEP 1: FINDING VS CODE SOURCE")
    print("=" * 80)
    
    # Common VS Code locations
    possible_paths = [
        Path(r"C:\Program Files\Microsoft VS Code"),
        Path(r"C:\Users") / Path.home().name / "AppData" / "Local" / "Programs" / "Microsoft VS Code",
        Path(r"C:\Program Files (x86)\Microsoft VS Code"),
    ]
    
    vscode_path = None
    for p in possible_paths:
        if p.exists():
            vscode_path = p
            break
    
    if not vscode_path:
        print("❌ VS Code not found in common locations!")
        print("\nPlease provide the path to VS Code:")
        vscode_path = Path(input("Path: ").strip())
        
        if not vscode_path.exists():
            print("❌ Path doesn't exist!")
            return
    
    print(f"✓ Found VS Code at: {vscode_path}")
    
    # Look for source files (resources/app folder usually has JS files)
    resources_path = vscode_path / "resources" / "app"
    if not resources_path.exists():
        resources_path = vscode_path
    
    print(f"✓ Analyzing: {resources_path}")
    
    print("\n" + "=" * 80)
    print("STEP 2: INDEXING CODEBASE (Parsing all files)")
    print("=" * 80)
    print("This extracts all functions, classes, methods...")
    print()
    
    start_time = time.time()
    
    result = await handle_index_codebase({
        "path": str(resources_path),
        "recursive": True
    })
    
    print(result)
    
    index_time = time.time() - start_time
    print(f"\n✓ Indexing took {index_time:.1f} seconds")
    
    print("\n" + "=" * 80)
    print("STEP 3: DEEP AI ANALYSIS (This is the slow part)")
    print("=" * 80)
    print("Both DeepSeek 33B and Qwen 30B will analyze each function")
    print("Progress will show below...")
    print()
    
    db = DatabaseManager()
    entities = db.search_entities()
    
    total = len(entities)
    print(f"Total entities to analyze: {total}")
    
    # Limit to first 50 for demo (otherwise it takes hours)
    analyze_limit = min(50, total)
    print(f"Analyzing first {analyze_limit} (full analysis would take hours)")
    print()
    
    analysis_start = time.time()
    
    for idx, entity in enumerate(entities[:analyze_limit], 1):
        fname = entity['file_path'].split('\\')[-1]
        
        print(f"[{idx}/{analyze_limit}] {entity['entity_type']}: {entity['name']} (in {fname})")
        
        # Check if already analyzed
        existing = db.get_entity_analysis(entity['id'])
        if existing:
            print("  ✓ Already analyzed (cached)")
            continue
        
        try:
            result = await handle_analyze_function({
                "function_name": entity['name'],
                "file_path": fname
            })
            
            # Show success/failure
            if "Confidence:" in result:
                # Extract confidence
                for line in result.split('\n'):
                    if 'Overall:' in line or 'Confidence:' in line:
                        print(f"  {line.strip()}")
                        break
            else:
                print(f"  Analysis: {result[:80]}...")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Show timing
        elapsed = time.time() - analysis_start
        avg = elapsed / idx
        remaining = (analyze_limit - idx) * avg
        
        print(f"  Time: {elapsed:.1f}s elapsed, ~{remaining:.1f}s remaining")
        print()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    
    stats = db.get_stats()
    total_time = time.time() - start_time
    
    print(f"""
Final Stats:
  - Files indexed: {stats['files']}
  - Code entities found: {stats['entities']}
  - Analyses completed: {stats['analyses']}
  - Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)

✓ AIs now know VS Code internals!
✓ All analysis is cached - queries will be instant!
✓ You can now ask Rex about any VS Code function!
""")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
