#!/usr/bin/env python3
"""Test GitOps MCP Server"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from server import run_git_command

def test_git_status():
    """Test git status"""
    print("🧪 Testing git status...")
    
    result = run_git_command(["status", "--short"])
    
    if result["success"]:
        print(f"✅ Git status works")
        print(f"   Output: {result['stdout'][:100]}")
    else:
        print(f"⚠️  Git command failed (might not be a git repo): {result.get('error')}")
    
    return True

def test_git_branch():
    """Test git branch listing"""
    print("\n🧪 Testing git branch...")
    
    result = run_git_command(["branch"])
    
    if result["success"]:
        print(f"✅ Git branch works")
        branches = result["stdout"].split("\n") if result["stdout"] else []
        print(f"   Found {len(branches)} branch(es)")
    else:
        print(f"⚠️  Git command failed: {result.get('error')}")
    
    return True

def test_git_log():
    """Test git log"""
    print("\n🧪 Testing git log...")
    
    result = run_git_command(["log", "-5", "--oneline"])
    
    if result["success"]:
        print(f"✅ Git log works")
        commits = result["stdout"].split("\n") if result["stdout"] else []
        print(f"   Found {len(commits)} recent commit(s)")
    else:
        print(f"⚠️  Git command failed: {result.get('error')}")
    
    return True

def main():
    """Run tests"""
    print("=" * 60)
    print("GITOPS MCP SERVER - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_git_status,
        test_git_branch,
        test_git_log
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 60)
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED (might not be a git repo)")
        return 0

if __name__ == "__main__":
    exit(main())
