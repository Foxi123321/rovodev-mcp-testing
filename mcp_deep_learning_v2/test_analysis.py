"""
Test deep analysis of the indexed code
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from server import handle_analyze_function, handle_query_codebase, handle_analyze_code
from database_manager import DatabaseManager

async def main():
    print("=" * 80)
    print("TESTING DEEP AI ANALYSIS")
    print("=" * 80)
    print()
    
    # Test 1: Analyze the login function from auth.py
    print("[TEST 1] Analyzing 'login' function from auth.py...")
    print("-" * 80)
    analysis1 = await handle_analyze_function({
        "function_name": "login",
        "file_path": "auth.py"
    })
    print(analysis1)
    print()
    
    # Test 2: Analyze hash_password function
    print("[TEST 2] Analyzing 'hash_password' function...")
    print("-" * 80)
    analysis2 = await handle_analyze_function({
        "function_name": "hash_password"
    })
    print(analysis2)
    print()
    
    # Test 3: Analyze UserManager class
    print("[TEST 3] Analyzing 'UserManager' class...")
    print("-" * 80)
    analysis3 = await handle_analyze_function({
        "function_name": "UserManager"
    })
    print(analysis3)
    print()
    
    # Test 4: Analyze code snippet
    print("[TEST 4] Analyzing custom code snippet...")
    print("-" * 80)
    test_code = """
def validate_user(username, password):
    if not username or not password:
        return False
    # Check against database
    user = db.get(username)
    return user and user.password == password
"""
    analysis4 = await handle_analyze_code({
        "code": test_code,
        "context": "User validation function",
        "language": "python"
    })
    print(analysis4)
    print()
    
    print("=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    
    # Show what's in the database now
    db = DatabaseManager()
    stats = db.get_stats()
    print(f"\nDatabase now has {stats['analyses']} analyses stored")
    print("These will be cached for instant future queries!")

if __name__ == "__main__":
    asyncio.run(main())
