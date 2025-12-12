"""
Demo: Analyze a single function to show how deep the AIs understand it
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from server import handle_analyze_function

async def main():
    print("=" * 80)
    print("DEMO: Deep AI Analysis of 'login' Function")
    print("=" * 80)
    print()
    print("Analyzing with DeepSeek (33B) + Qwen (30B)...")
    print("This takes 5-10 seconds...\n")
    
    result = await handle_analyze_function({
        "function_name": "login",
        "file_path": "auth.py"
    })
    
    print(result)
    print()
    print("=" * 80)
    print("This analysis is now CACHED!")
    print("Next time you ask about 'login', it's instant!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
