"""
Test Visual Testing Feature
Tests the full pipeline: Browser -> Screenshot -> Llava -> Validation
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visual_tester import VisualTester

print("=" * 60)
print("REX VISUAL TESTING - DEMONSTRATION")
print("=" * 60)

# Mock MCP clients for testing
class MockBrowserClient:
    """Mock browser client for testing without actual MCP connection"""
    
    async def navigate(self, url):
        print(f"  🌐 Navigating to: {url}")
        return {"status": "success", "message": "Navigation successful"}
    
    async def screenshot(self, name):
        print(f"  📸 Taking screenshot: {name}")
        # In real implementation, this would take actual screenshot
        return {
            "status": "success",
            "path": f"screenshots/{name}.png",
            "message": "Screenshot captured"
        }
    
    async def execute_js(self, script):
        print(f"  ⚡ Executing JS: {script[:50]}...")
        return {"status": "success", "result": None}
    
    async def click(self, selector):
        print(f"  🖱️  Clicking: {selector}")
        return {"status": "success"}
    
    async def fill(self, selector, value):
        print(f"  ⌨️  Filling {selector} with: {value}")
        return {"status": "success"}


class MockVisionClient:
    """Mock vision client for testing"""
    
    async def analyze_image(self, image_path, prompt):
        print(f"  👁️  Analyzing image with Llava...")
        print(f"     Image: {image_path}")
        print(f"     Prompt: {prompt[:80]}...")
        
        # Mock Llava response
        analysis = """
        I can see a login page with the following elements:
        
        1. A large heading that says "Rex Task Orchestrator Test Page" with fire emojis
        2. Two input fields - one for username and one for password
        3. Three buttons:
           - A green "Login" button
           - A blue "Sign Up" button  
           - A red "Reset" button
        4. An output area below the buttons
        5. The page has a purple gradient background
        
        Comparison to expected:
        YES - This matches the expected description. The page has login functionality with username/password fields and three colored action buttons.
        
        Confidence: 0.85
        
        All interactive elements are present and correctly styled.
        """
        
        return analysis


# Monkey patch the VisualTester methods to use mock clients
async def mock_call_browser(self, tool_name, tool_input):
    """Mock browser call"""
    if tool_name == "browser_navigate":
        return await mock_browser.navigate(tool_input["url"])
    elif tool_name == "browser_screenshot":
        return await mock_browser.screenshot(tool_input["name"])
    elif tool_name == "browser_execute_js":
        return await mock_browser.execute_js(tool_input["script"])
    elif tool_name == "browser_click":
        return await mock_browser.click(tool_input["selector"])
    elif tool_name == "browser_fill":
        return await mock_browser.fill(tool_input["selector"], tool_input["value"])

async def mock_call_vision(self, tool_name, tool_input):
    """Mock vision call"""
    return await mock_vision.analyze_image(tool_input["image_path"], tool_input["prompt"])


# Create mock clients
mock_browser = MockBrowserClient()
mock_vision = MockVisionClient()

# Initialize visual tester
config = {
    "screenshot_dir": "screenshots",
    "analysis_confidence_threshold": 0.7,
    "auto_retry_on_mismatch": False,
    "max_visual_retries": 2
}

visual_tester = VisualTester(config, {})

# Patch methods
visual_tester._call_browser = lambda tool, inp: mock_call_browser(visual_tester, tool, inp)
visual_tester._call_vision = lambda tool, inp: mock_call_vision(visual_tester, tool, inp)

print("\n[TEST] Running Visual Test")
print("-" * 60)

async def run_test():
    # Get absolute path to test page
    test_page_path = os.path.join(os.path.dirname(__file__), "test_page.html")
    test_url = f"file:///{test_page_path.replace(chr(92), '/')}"
    
    result = await visual_tester.run_visual_test(
        url=test_url,
        expected_description="A login page with username and password fields, and three colored buttons (green Login, blue Sign Up, red Reset)",
        test_id="demo_test_001",
        elements_to_test=[
            {
                "selector": "#username",
                "action": "fill",
                "value": "testuser"
            },
            {
                "selector": "#btn-primary",
                "action": "click"
            }
        ]
    )
    
    print("\n" + "=" * 60)
    print("VISUAL TEST RESULTS")
    print("=" * 60)
    
    print(f"\n✅ Test ID: {result.test_id}")
    print(f"🌐 URL: {result.url}")
    print(f"📸 Screenshot: {result.screenshot_path}")
    print(f"\n📝 Expected:")
    print(f"   {result.expected_description}")
    
    print(f"\n🤖 Llava Analysis:")
    print(f"   {result.llava_analysis[:200]}...")
    
    print(f"\n🎯 Result: {'✅ PASSED' if result.passed else '❌ FAILED'}")
    print(f"📊 Confidence: {result.confidence:.2%}")
    print(f"⏱️  Duration: {result.duration:.2f}s")
    
    if result.errors:
        print(f"\n⚠️  Errors:")
        for error in result.errors:
            print(f"   - {error}")
    
    # Get stats
    stats = visual_tester.get_test_stats()
    print(f"\n📊 Overall Stats:")
    print(f"   Total Tests: {stats['total_tests']}")
    print(f"   Passed: {stats['passed']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Pass Rate: {stats['pass_rate']:.1%}")
    print(f"   Avg Confidence: {stats['avg_confidence']:.1%}")
    print(f"   Avg Duration: {stats['avg_duration']:.2f}s")

asyncio.run(run_test())

print("\n" + "=" * 60)
print("🔥 VISUAL TESTING DEMO COMPLETE! 🔥")
print("=" * 60)
print("\nThis demonstrates:")
print("  ✅ Browser navigation")
print("  ✅ Screenshot capture")
print("  ✅ Llava AI analysis")
print("  ✅ Expected vs actual comparison")
print("  ✅ Interactive element testing")
print("  ✅ Confidence scoring")
print("\nIn production, this connects to real MCP servers!")
print("=" * 60)
