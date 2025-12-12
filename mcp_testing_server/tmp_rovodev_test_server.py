"""Test script for MCP server functionality."""
import asyncio
import json
from server import browser_tester, code_reviewer, app_tester, image_analyzer

async def test_browser():
    """Test browser automation."""
    print("\n=== Testing Browser Automation ===")
    
    # Test navigation
    print("1. Testing browser navigation...")
    result = await browser_tester.navigate("https://example.com")
    print(f"   Navigate result: {json.dumps(result, indent=2)}")
    
    # Test screenshot
    print("\n2. Testing screenshot capture...")
    result = await browser_tester.get_screenshot("test_screenshot")
    print(f"   Screenshot result: {json.dumps(result, indent=2)}")
    
    # Test JS execution
    print("\n3. Testing JavaScript execution...")
    result = await browser_tester.evaluate_js("document.title")
    print(f"   JS execution result: {json.dumps(result, indent=2)}")
    
    # Test console errors
    print("\n4. Testing console error retrieval...")
    result = await browser_tester.get_console_errors()
    print(f"   Console errors: {len(result.get('errors', []))} errors, {len(result.get('warnings', []))} warnings")
    
    # Close browser
    print("\n5. Closing browser...")
    result = await browser_tester.close()
    print(f"   Close result: {json.dumps(result, indent=2)}")

def test_code_review():
    """Test code review functionality."""
    print("\n=== Testing Code Review ===")
    print("Reviewing server.py...")
    result = code_reviewer.review_file("server.py")
    print(f"Security issues: {len(result.get('security_issues', []))}")
    print(f"Bug risks: {len(result.get('bug_risks', []))}")
    print(f"Code smells: {len(result.get('code_smells', []))}")
    print(f"Total lines: {result.get('stats', {}).get('total_lines', 0)}")

def test_app_tester():
    """Test desktop app functionality."""
    print("\n=== Testing Desktop App Tools ===")
    
    print("1. Getting mouse position...")
    result = app_tester.get_mouse_position()
    print(f"   Mouse position: {json.dumps(result, indent=2)}")
    
    print("\n2. Getting screen size...")
    result = app_tester.get_screen_size()
    print(f"   Screen size: {json.dumps(result, indent=2)}")

async def main():
    """Run all tests."""
    print("="*60)
    print("MCP Testing & Review Server - Functionality Test")
    print("="*60)
    
    # Test code review (sync)
    test_code_review()
    
    # Test app tester (sync)
    test_app_tester()
    
    # Test browser automation (async)
    await test_browser()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
