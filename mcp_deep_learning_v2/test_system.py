"""
Test script for Deep Learning Intelligence v2
Tests all components independently
"""

import asyncio
import sys
from pathlib import Path

print("=" * 60)
print("Deep Learning Intelligence v2 - System Test")
print("=" * 60)
print()

# Test 1: Config
print("[1/7] Testing configuration...")
try:
    from config import (
        OLLAMA_BASE_URL,
        PRIMARY_MODEL,
        SECONDARY_MODEL,
        DATA_DIR,
        DB_PATH
    )
    print(f"  ✓ Ollama URL: {OLLAMA_BASE_URL}")
    print(f"  ✓ Primary Model: {PRIMARY_MODEL}")
    print(f"  ✓ Secondary Model: {SECONDARY_MODEL}")
    print(f"  ✓ Data Directory: {DATA_DIR}")
except Exception as e:
    print(f"  ✗ Config error: {e}")
    sys.exit(1)

# Test 2: Database
print("\n[2/7] Testing database...")
try:
    from database_manager import DatabaseManager
    db = DatabaseManager()
    stats = db.get_stats()
    print(f"  ✓ Database initialized")
    print(f"  ✓ Files indexed: {stats['files']}")
    print(f"  ✓ Entities: {stats['entities']}")
except Exception as e:
    print(f"  ✗ Database error: {e}")
    sys.exit(1)

# Test 3: Code Parser
print("\n[3/7] Testing code parser...")
try:
    from code_parser import CodeParser
    parser = CodeParser()
    
    # Test on this file
    test_file = Path(__file__)
    result = parser.parse_file(test_file)
    
    print(f"  ✓ Parser initialized")
    print(f"  ✓ Parsed test file: {result['language']}")
    print(f"  ✓ Found {len(result.get('entities', []))} entities")
except Exception as e:
    print(f"  ✗ Parser error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Vector Store
print("\n[4/7] Testing vector store...")
try:
    from vector_store import VectorStore
    vector_store = VectorStore()
    stats = vector_store.get_stats()
    
    print(f"  ✓ Vector store initialized")
    print(f"  ✓ Enabled: {stats['enabled']}")
    print(f"  ✓ Vectors: {stats['total_vectors']}")
except Exception as e:
    print(f"  ✗ Vector store error: {e}")

# Test 5: Consensus Engine
print("\n[5/7] Testing consensus engine...")
try:
    from consensus_engine import ConsensusEngine
    
    # Test similarity
    text1 = "This function validates user input"
    text2 = "This validates input from users"
    similarity = ConsensusEngine.compute_text_similarity(text1, text2)
    
    print(f"  ✓ Consensus engine initialized")
    print(f"  ✓ Similarity test: {similarity:.2%}")
except Exception as e:
    print(f"  ✗ Consensus error: {e}")

# Test 6: Ollama Connection
print("\n[6/7] Testing Ollama connection...")
async def test_ollama():
    try:
        from ollama_client import OllamaClient
        
        async with OllamaClient() as client:
            # Check models
            primary_ok = await client.check_model_available(PRIMARY_MODEL)
            secondary_ok = await client.check_model_available(SECONDARY_MODEL)
            
            print(f"  ✓ Ollama connection OK")
            print(f"  {'✓' if primary_ok else '✗'} Primary model ({PRIMARY_MODEL}): {'Available' if primary_ok else 'NOT FOUND'}")
            print(f"  {'✓' if secondary_ok else '✗'} Secondary model ({SECONDARY_MODEL}): {'Available' if secondary_ok else 'NOT FOUND'}")
            
            if not primary_ok:
                print(f"\n  WARNING: Run 'ollama pull {PRIMARY_MODEL}'")
            if not secondary_ok:
                print(f"  WARNING: Run 'ollama pull {SECONDARY_MODEL}'")
            
            return primary_ok and secondary_ok
    except Exception as e:
        print(f"  ✗ Ollama error: {e}")
        print(f"  Make sure Ollama is running!")
        return False

ollama_ok = asyncio.run(test_ollama())

# Test 7: Quick Analysis Test
if ollama_ok:
    print("\n[7/7] Testing AI analysis...")
    async def test_analysis():
        try:
            from ollama_client import OllamaClient
            from consensus_engine import ConsensusEngine
            
            test_code = "def add(a, b):\n    return a + b"
            
            async with OllamaClient() as client:
                result = await client.analyze_code_dual(
                    code=test_code,
                    context="Simple test function",
                    technical_prompt="Analyze this code briefly: {code}",
                    semantic_prompt="What is the purpose of this code: {code}"
                )
                
                consensus = ConsensusEngine.merge_analyses(
                    result["primary"],
                    result["secondary"]
                )
                
                print(f"  ✓ Dual-AI analysis complete")
                print(f"  ✓ Agreement: {consensus['agreement_score']:.0%}")
                print(f"  ✓ Confidence: {consensus['consensus_confidence']:.0%}")
                print(f"  ✓ Mode: {consensus['mode']}")
                
                # Show a snippet of the analysis
                summary = consensus['consensus_summary'][:100]
                print(f"  ✓ Sample output: {summary}...")
                
        except Exception as e:
            print(f"  ✗ Analysis error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_analysis())
else:
    print("\n[7/7] Skipping AI analysis test (Ollama not ready)")

# Summary
print("\n" + "=" * 60)
print("System Test Complete!")
print("=" * 60)

if ollama_ok:
    print("\n✓ All systems operational!")
    print("\nYou can now:")
    print("  1. Run the MCP server: python server.py")
    print("  2. Use it with RovoDev through MCP")
    print("  3. Let Rex analyze your code like a boss!")
else:
    print("\n⚠ Ollama models not ready")
    print("\nNext steps:")
    print("  1. Ensure Ollama is running: ollama serve")
    print(f"  2. Pull models: ollama pull {PRIMARY_MODEL}")
    print(f"  3. Pull models: ollama pull {SECONDARY_MODEL}")
    print("  4. Run this test again")

print()
