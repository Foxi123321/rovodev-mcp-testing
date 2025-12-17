"""Tests for Phase 2: Exploration Loop."""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase2_exploration_loop import ExplorationLoop
from schemas import create_exploration_goal


async def test_exploration_loop():
    """Test basic exploration loop execution."""
    print("🧪 Testing exploration loop...")
    
    loop = ExplorationLoop()
    
    # Create a test goal
    goal = create_exploration_goal(
        goal_id="test_1",
        goal_type="discovery",
        description="Discover website structure"
    )
    
    goal["success_criteria"]["must_have"] = ["structure", "navigation"]
    goal["constraints"]["max_time_seconds"] = 30
    goal["constraints"]["max_attempts"] = 3
    
    # Run exploration
    result = await loop.explore(
        url="https://example.com",
        goal=goal
    )
    
    print(f"\n📊 Exploration Result:")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['iterations']}")
    print(f"   Patterns learned: {len(result['learned_patterns'])}")
    
    # Get statistics
    stats = loop.get_loop_statistics()
    print(f"\n📈 Loop Statistics:")
    print(f"   Total iterations: {stats['total_iterations']}")
    print(f"   Success rate: {stats['success_rate']:.0%}")
    print(f"   Strategies used: {stats['strategies_used']}")
    
    return result['iterations'] > 0


async def test_decision_system():
    """Test decision making."""
    print("\n🧪 Testing decision system...")
    
    from phase2_exploration_loop import DecisionSystem
    from schemas import create_empty_website_state, create_exploration_goal
    
    decision_system = DecisionSystem()
    
    state = create_empty_website_state("https://example.com")
    goal = create_exploration_goal("test_2", "data_extraction", "Extract products")
    
    # Test decision with low confidence
    state["confidence"]["overall"] = 0.3
    decision = decision_system.decide_next_action(state, goal, [])
    
    print(f"   Decision with low confidence: {decision['action']}")
    print(f"   Strategy: {decision['strategy']}")
    print(f"   Reasoning: {decision['reasoning']}")
    
    return decision["action"] == "explore_more"


async def test_perception_system():
    """Test perception system."""
    print("\n🧪 Testing perception system...")
    
    from phase2_exploration_loop import PerceptionSystem
    
    perception = PerceptionSystem()
    
    # Test perception
    perceptions = await perception.perceive("https://example.com")
    
    print(f"   Perceptions collected:")
    print(f"     - DOM: {perceptions['dom'] is not None}")
    print(f"     - Network: {perceptions['network'] is not None}")
    print(f"     - Visual: {perceptions['visual'] is not None}")
    print(f"     - Knowledge: {perceptions['knowledge'] is not None}")
    
    # Test fusion
    fused = perception.fuse_perceptions(perceptions)
    
    print(f"   Fused understanding created: ✅")
    print(f"     - Structure: {fused['structure'] is not None}")
    print(f"     - Capabilities: {fused['capabilities'] is not None}")
    print(f"     - Confidence: {fused['confidence']['overall']:.0%}")
    
    return fused is not None


async def run_all_tests():
    """Run all Phase 2 tests."""
    print("="*60)
    print("PHASE 2: EXPLORATION LOOP - TESTS")
    print("="*60)
    
    tests = [
        test_perception_system,
        test_decision_system,
        test_exploration_loop
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
