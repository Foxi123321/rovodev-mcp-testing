"""Tests for Phase 1: Mental Models schemas."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from schemas import (
    validate_website_state,
    create_empty_website_state,
    validate_exploration_goal,
    create_exploration_goal
)


def test_empty_website_state():
    """Test creating and validating an empty website state."""
    print("🧪 Testing empty website state creation...")
    
    state = create_empty_website_state("https://example.com")
    is_valid, errors = validate_website_state(state)
    
    if is_valid:
        print("✅ Empty website state is valid")
        return True
    else:
        print(f"❌ Empty website state is invalid: {errors}")
        return False


def test_exploration_goal():
    """Test creating and validating an exploration goal."""
    print("\n🧪 Testing exploration goal creation...")
    
    goal = create_exploration_goal(
        goal_id="test_goal_1",
        goal_type="data_extraction",
        description="Extract product listings"
    )
    
    is_valid, errors = validate_exploration_goal(goal)
    
    if is_valid:
        print("✅ Exploration goal is valid")
        return True
    else:
        print(f"❌ Exploration goal is invalid: {errors}")
        return False


def test_website_state_with_data():
    """Test website state with actual data."""
    print("\n🧪 Testing website state with data...")
    
    state = create_empty_website_state("https://example.com")
    
    # Add some data
    state["structure"]["dom_summary"]["total_elements"] = 150
    state["structure"]["dom_summary"]["links"] = 25
    state["structure"]["navigation"].append({
        "text": "Home",
        "url": "/",
        "type": "menu"
    })
    
    state["capabilities"]["ui_interactions"].append({
        "action": "click",
        "target": ".search-button",
        "success_rate": 0.95
    })
    
    state["confidence"]["overall"] = 0.7
    state["confidence"]["breakdown"]["structure"] = 0.8
    state["confidence"]["breakdown"]["capabilities"] = 0.6
    state["confidence"]["breakdown"]["api_knowledge"] = 0.5
    
    is_valid, errors = validate_website_state(state)
    
    if is_valid:
        print("✅ Website state with data is valid")
        print(f"   Confidence: {state['confidence']['overall']}")
        print(f"   Navigation items: {len(state['structure']['navigation'])}")
        print(f"   UI interactions: {len(state['capabilities']['ui_interactions'])}")
        return True
    else:
        print(f"❌ Website state with data is invalid: {errors}")
        return False


def test_invalid_website_state():
    """Test validation catches invalid state."""
    print("\n🧪 Testing invalid website state detection...")
    
    # Missing required fields
    invalid_state = {
        "url": "https://example.com"
        # Missing: timestamp, structure, capabilities, confidence
    }
    
    is_valid, errors = validate_website_state(invalid_state)
    
    if not is_valid and len(errors) > 0:
        print(f"✅ Correctly detected {len(errors)} validation errors")
        return True
    else:
        print("❌ Failed to detect invalid state")
        return False


def run_all_tests():
    """Run all Phase 1 tests."""
    print("="*60)
    print("PHASE 1: MENTAL MODELS - SCHEMA TESTS")
    print("="*60)
    
    tests = [
        test_empty_website_state,
        test_exploration_goal,
        test_website_state_with_data,
        test_invalid_website_state
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results.append(False)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
