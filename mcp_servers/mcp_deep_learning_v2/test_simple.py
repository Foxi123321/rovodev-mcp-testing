"""Simple direct test"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp_knowledge_db"))

from database import KnowledgeDatabase
from models import CodeFile, CodeKnowledge

print("🧪 Simple Direct Test")
print("=" * 70)
print()

# Test 1: Store file
print("Test 1: Store File")
db = KnowledgeDatabase()

code_file = CodeFile(
    file_path="C:\\test\\example2.py",
    project_name="test_project",
    language="python",
    size_bytes=2048,
    checksum="abc123"
)

try:
    file_id = db.store_code_file(code_file)
    print(f"✅ File stored with ID: {file_id}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Store knowledge
print("Test 2: Store Code Knowledge")

code_knowledge = CodeKnowledge(
    file_id=file_id,
    symbol_name="my_function",
    symbol_type="function",
    line_start=10,
    line_end=20,
    purpose="Test function",
    complexity="simple",
    parameters='["x", "y"]',
    return_type="int",
    docstring="A test",
    code_snippet="def my_function(x, y):\n    return x + y"
)

try:
    knowledge_id = db.store_code_knowledge(code_knowledge)
    print(f"✅ Knowledge stored with ID: {knowledge_id}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Query it back
print("Test 3: Query Back")
try:
    results = db.query_code_knowledge("my_function", limit=5)
    if results:
        print(f"✅ Found {len(results)} results")
        for r in results:
            print(f"   - {r['symbol_name']}: {r['purpose']}")
    else:
        print("⚠️  No results")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

db.close()
print()
print("✅ Test complete!")
