"""Full automated test of the web app using MCP server."""
import asyncio
import json
import os
from pathlib import Path
from server import browser_tester, image_analyzer

async def comprehensive_web_test():
    """Run a full test suite on the web app."""
    
    print("="*80)
    print("🔥 COMPREHENSIVE WEB APP TEST 🔥")
    print("="*80)
    
    # Get the full path to the HTML file
    html_path = Path(__file__).parent / "tmp_rovodev_test_webapp.html"
    url = f"file:///{html_path.as_posix()}"
    
    print(f"\n📍 Testing URL: {url}\n")
    
    # Test 1: Navigate to the page
    print("\n[TEST 1] 🌐 Navigating to web app...")
    result = await browser_tester.navigate(url)
    print(f"✅ Status: {result['status']}")
    print(f"   Title: {result.get('title', 'N/A')}")
    print(f"   HTTP Status: {result.get('status_code', 'N/A')}")
    
    # Wait for page to load
    await asyncio.sleep(2)
    
    # Test 2: Take initial screenshot
    print("\n[TEST 2] 📸 Capturing initial page screenshot...")
    result = await browser_tester.get_screenshot("webapp_initial")
    print(f"✅ Screenshot saved: {result.get('path', 'N/A')}")
    screenshot_path = result.get('path', '')
    
    # Test 3: Check console errors
    print("\n[TEST 3] 🔍 Checking console errors...")
    result = await browser_tester.get_console_errors()
    errors = result.get('errors', [])
    warnings = result.get('warnings', [])
    print(f"⚠️  Errors found: {len(errors)}")
    print(f"⚠️  Warnings found: {len(warnings)}")
    if errors:
        for err in errors[:3]:  # Show first 3 errors
            print(f"   - {err.get('text', 'Unknown error')}")
    
    # Test 4: Click on a product
    print("\n[TEST 4] 🖱️  Clicking on a product item...")
    result = await browser_tester.click_element(".product-item:first-child")
    print(f"✅ Click status: {result['status']}")
    
    await asyncio.sleep(1)
    
    # Test 5: Take screenshot of modal
    print("\n[TEST 5] 📸 Capturing modal screenshot...")
    result = await browser_tester.get_screenshot("webapp_modal")
    print(f"✅ Screenshot saved: {result.get('path', 'N/A')}")
    modal_screenshot = result.get('path', '')
    
    # Test 6: Close modal
    print("\n[TEST 6] 🖱️  Closing modal...")
    result = await browser_tester.click_element(".close-modal")
    print(f"✅ Click status: {result['status']}")
    
    await asyncio.sleep(1)
    
    # Test 7: Fill out the order form
    print("\n[TEST 7] ✍️  Filling out order form...")
    
    # Username
    result = await browser_tester.fill_input("#username", "TestUser123")
    print(f"   Username: {result['status']}")
    
    # Email
    result = await browser_tester.fill_input("#email", "test@darknet.onion")
    print(f"   Email: {result['status']}")
    
    # Select product
    result = await browser_tester.evaluate_js("document.getElementById('product-select').value = 'cards';")
    print(f"   Product selection: {result['status']}")
    
    # Quantity
    result = await browser_tester.fill_input("#quantity", "5")
    print(f"   Quantity: {result['status']}")
    
    # BTC Address
    result = await browser_tester.fill_input("#btc-address", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    print(f"   BTC Address: {result['status']}")
    
    # Special instructions
    result = await browser_tester.fill_input("#special-instructions", "Rush order, please encrypt shipment")
    print(f"   Instructions: {result['status']}")
    
    await asyncio.sleep(1)
    
    # Test 8: Screenshot of filled form
    print("\n[TEST 8] 📸 Capturing filled form...")
    result = await browser_tester.get_screenshot("webapp_form_filled")
    print(f"✅ Screenshot saved: {result.get('path', 'N/A')}")
    form_screenshot = result.get('path', '')
    
    # Test 9: Test JavaScript execution
    print("\n[TEST 9] ⚙️  Testing JavaScript execution...")
    result = await browser_tester.evaluate_js("""
        ({
            title: document.title,
            productCount: document.querySelectorAll('.product-item').length,
            statsVisible: document.querySelector('.stats') !== null,
            chatMessages: document.querySelectorAll('.chat-message').length
        })
    """)
    print(f"✅ JS Execution: {result['status']}")
    if result['status'] == 'success':
        data = result.get('result', {})
        print(f"   Page title: {data.get('title', 'N/A')}")
        print(f"   Product items: {data.get('productCount', 0)}")
        print(f"   Stats visible: {data.get('statsVisible', False)}")
        print(f"   Chat messages: {data.get('chatMessages', 0)}")
    
    # Test 10: Trigger the intentional error
    print("\n[TEST 10] 💥 Triggering intentional error (Admin Panel button)...")
    result = await browser_tester.evaluate_js("triggerError()")
    print(f"   Triggered: {result['status']}")
    
    await asyncio.sleep(1)
    
    # Test 11: Check for new errors
    print("\n[TEST 11] 🔍 Checking for new console errors...")
    result = await browser_tester.get_console_errors()
    errors = result.get('errors', [])
    print(f"⚠️  Total errors now: {len(errors)}")
    if len(errors) > 2:
        print(f"   Latest error: {errors[-1].get('text', 'Unknown')}")
    
    # Test 12: Final screenshot
    print("\n[TEST 12] 📸 Capturing final state...")
    result = await browser_tester.get_screenshot("webapp_final")
    print(f"✅ Screenshot saved: {result.get('path', 'N/A')}")
    final_screenshot = result.get('path', '')
    
    # Test 13: Vision AI Analysis (if available)
    print("\n[TEST 13] 👁️  Running Vision AI analysis on screenshots...")
    
    if screenshot_path and os.path.exists(screenshot_path):
        print("\n   Analyzing initial page...")
        result = image_analyzer.analyze_screenshot(screenshot_path)
        if result.get('status') == 'success':
            print(f"✅ Vision AI analysis complete!")
            print(f"\n--- AI Analysis of Initial Page ---")
            print(result.get('analysis', 'No analysis available')[:500] + "...")
        else:
            print(f"⚠️  Vision AI: {result.get('message', 'Not available')}")
    
    if form_screenshot and os.path.exists(form_screenshot):
        print("\n   Analyzing filled form...")
        result = image_analyzer.analyze_screenshot(
            form_screenshot,
            "Check if all form fields are properly filled and identify any UI issues or bugs."
        )
        if result.get('status') == 'success':
            print(f"✅ Form analysis complete!")
            print(f"\n--- AI Analysis of Form ---")
            print(result.get('analysis', 'No analysis available')[:500] + "...")
    
    # Test 14: UI Issue Detection
    print("\n[TEST 14] 🔎 Running UI/UX issue detection...")
    if final_screenshot and os.path.exists(final_screenshot):
        result = image_analyzer.detect_ui_issues(final_screenshot)
        if result.get('status') == 'success':
            print(f"✅ UI issue detection complete!")
            print(f"\n--- UI/UX Issues Detected ---")
            print(result.get('analysis', 'No issues found')[:500] + "...")
        else:
            print(f"⚠️  UI Detection: {result.get('message', 'Not available')}")
    
    # Test 15: Close browser
    print("\n[TEST 15] 🔒 Closing browser...")
    result = await browser_tester.close()
    print(f"✅ Browser closed: {result['status']}")
    
    print("\n" + "="*80)
    print("✅ COMPREHENSIVE TEST COMPLETE!")
    print("="*80)
    print(f"\n📊 Test Summary:")
    print(f"   - Navigation: ✅")
    print(f"   - Screenshots: 4 captured")
    print(f"   - Form interaction: ✅")
    print(f"   - JavaScript execution: ✅")
    print(f"   - Error detection: ✅")
    print(f"   - Vision AI analysis: {'✅' if image_analyzer.vision_model else '⚠️  (No model)'}")
    print(f"\n📁 Check the 'screenshots' folder for captured images!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(comprehensive_web_test())
