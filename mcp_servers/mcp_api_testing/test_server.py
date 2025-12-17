#!/usr/bin/env python3
"""Test the API Testing MCP Server"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from server import (
    generate_request_id,
    save_recording,
    load_recording,
    save_schema,
    load_schema,
    validate_against_schema
)

def test_recording():
    """Test recording functionality"""
    print("🧪 Testing API Recording...")
    
    recording = {
        "request_id": "test123",
        "timestamp": "2025-12-15T10:00:00",
        "request": {
            "method": "GET",
            "url": "https://api.example.com/users/1",
            "headers": {"Authorization": "Bearer token"},
            "body": None
        },
        "response": {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"id": 1, "name": "Test User", "email": "test@example.com"}
        },
        "tags": ["users", "test"]
    }
    
    # Save recording
    filepath = save_recording(recording)
    print(f"✅ Saved recording to: {filepath}")
    
    # Load recording
    loaded = load_recording("test123")
    assert loaded is not None, "Failed to load recording"
    assert loaded["request"]["method"] == "GET", "Method mismatch"
    print(f"✅ Loaded recording: {loaded['request']['method']} {loaded['request']['url']}")
    
    return True

def test_schema_validation():
    """Test schema validation"""
    print("\n🧪 Testing Schema Validation...")
    
    # Save a schema
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"}
        },
        "required": ["id", "name"]
    }
    
    filepath = save_schema("user_schema", schema)
    print(f"✅ Saved schema to: {filepath}")
    
    # Load schema
    loaded_schema = load_schema("user_schema")
    assert loaded_schema is not None, "Failed to load schema"
    print(f"✅ Loaded schema: {loaded_schema['type']}")
    
    # Validate valid data
    valid_data = {"id": 1, "name": "John", "email": "john@example.com"}
    result = validate_against_schema(valid_data, schema)
    assert result["valid"], f"Valid data failed: {result['errors']}"
    print(f"✅ Valid data passed validation")
    
    # Validate invalid data (missing required field)
    invalid_data = {"id": 1, "email": "john@example.com"}  # Missing 'name'
    result = validate_against_schema(invalid_data, schema)
    assert not result["valid"], "Invalid data should fail"
    print(f"✅ Invalid data correctly failed: {result['errors']}")
    
    # Validate type mismatch
    type_mismatch = {"id": "not_a_number", "name": "John"}
    result = validate_against_schema(type_mismatch, schema)
    assert not result["valid"], "Type mismatch should fail"
    print(f"✅ Type mismatch detected: {result['errors']}")
    
    return True

def test_request_id_generation():
    """Test request ID generation"""
    print("\n🧪 Testing Request ID Generation...")
    
    id1 = generate_request_id("GET", "https://api.example.com/users", None)
    id2 = generate_request_id("GET", "https://api.example.com/users", None)
    id3 = generate_request_id("POST", "https://api.example.com/users", {"name": "test"})
    
    assert id1 == id2, "Same request should generate same ID"
    assert id1 != id3, "Different requests should generate different IDs"
    
    print(f"✅ Request ID 1: {id1}")
    print(f"✅ Request ID 2: {id2} (matches)")
    print(f"✅ Request ID 3: {id3} (different)")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("API TESTING MCP SERVER - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_request_id_generation,
        test_recording,
        test_schema_validation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
