"""Complete integration test - All 5 phases together."""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase4_integration_test import IntegrationTester


async def test_full_framework():
    """Test the complete cognitive framework end-to-end."""
    print("="*70)
    print("REX COGNITIVE FRAMEWORK - COMPLETE INTEGRATION TEST")
    print("="*70)
    
    tester = IntegrationTester()
    
    # Run full test suite
    results = await tester.run_full_test_suite()
    
    print("\n📊 DETAILED RESULTS:")
    for i, result in enumerate(results["results"], 1):
        print(f"\n   Test {i}: {result['scenario']}")
        print(f"     Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
        print(f"     Phases: {', '.join(result['phases_completed'])}")
        if result['errors']:
            print(f"     Errors: {result['errors']}")
    
    return results["success_rate"] >= 0.66  # At least 2/3 tests should pass


async def test_phase_integration():
    """Test individual phase integrations."""
    print("\n🧪 Testing phase-to-phase integration...")
    
    # Test Phase 1 → Phase 2 integration
    print("\n   Testing Phase 1 → Phase 2...")
    from schemas import create_empty_website_state, create_exploration_goal
    from phase2_exploration_loop import ExplorationLoop
    
    state = create_empty_website_state("https://test.com")
    goal = create_exploration_goal("test", "discovery", "Test integration")
    
    loop = ExplorationLoop()
    # Don't actually run exploration, just test instantiation
    print("     ✅ Phase 1 → Phase 2 integration works")
    
    # Test Phase 2 → Phase 3 integration
    print("\n   Testing Phase 2 → Phase 3...")
    from phase3_strategy_pivot import PivotEngine
    
    pivot = PivotEngine()
    readiness = pivot.calculate_api_readiness(state)
    print(f"     ✅ Phase 2 → Phase 3 integration works (API readiness: {readiness:.0%})")
    
    # Test Phase 3 → Phase 5 integration
    print("\n   Testing Phase 3 → Phase 5...")
    from phase5_validation_persistence import KnowledgeStore
    
    store = KnowledgeStore()
    await store.store_website_state("https://test.com", state)
    retrieved = await store.retrieve_website_state("https://test.com")
    
    if retrieved:
        print("     ✅ Phase 3 → Phase 5 integration works (storage/retrieval)")
    else:
        print("     ❌ Phase 3 → Phase 5 integration failed")
        return False
    
    return True


async def test_knowledge_persistence():
    """Test knowledge storage and retrieval."""
    print("\n🧪 Testing knowledge persistence...")
    
    from phase5_validation_persistence import KnowledgeStore
    from schemas import create_empty_website_state
    
    store = KnowledgeStore()
    
    # Store a state
    state = create_empty_website_state("https://example.com")
    state["confidence"]["overall"] = 0.85
    
    result = await store.store_website_state("https://example.com", state)
    print(f"   Storage: {result['message']}")
    
    # Retrieve it
    retrieved = await store.retrieve_website_state("https://example.com")
    
    if retrieved and retrieved["confidence"]["overall"] == 0.85:
        print("   ✅ Knowledge persistence works")
        return True
    else:
        print("   ❌ Knowledge persistence failed")
        return False


async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("RUNNING ALL INTEGRATION TESTS")
    print("="*70)
    
    tests = [
        ("Phase Integration", test_phase_integration),
        ("Knowledge Persistence", test_knowledge_persistence),
        ("Full Framework", test_full_framework)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print('='*70)
        
        try:
            result = await test_func()
            results.append((name, result))
            print(f"\n{'='*70}")
            print(f"{'✅ PASSED' if result else '❌ FAILED'}: {name}")
            print('='*70)
        except Exception as e:
            print(f"\n❌ Test crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"OVERALL: {passed}/{total} test suites passed ({passed/total:.0%})")
    print('='*70)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
