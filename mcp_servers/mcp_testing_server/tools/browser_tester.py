"""Browser automation tools using Playwright for testing."""
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class BrowserTester:
    """Controls browser for testing websites and web apps."""
    
    # Class-level variables to persist across calls
    _shared_browser = None
    _shared_context = None
    _shared_page = None
    _shared_playwright = None
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console_logs = []
        self.screenshots_dir = Path(config['screenshots']['path'])
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # ALWAYS use class-level shared instances
        if BrowserTester._shared_browser is not None:
            print(f"[DEBUG] __init__: Reusing existing browser instance")
            self.browser = BrowserTester._shared_browser
            self.context = BrowserTester._shared_context
            self.page = BrowserTester._shared_page
            self.playwright = BrowserTester._shared_playwright
        else:
            print(f"[DEBUG] __init__: No existing browser, starting fresh")
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
    
    async def initialize(self):
        """Initialize Playwright browser."""
        print("[DEBUG] initialize() called")
        try:
            from playwright.async_api import async_playwright
            print("[DEBUG] Starting playwright...")
            self.playwright = await async_playwright().start()
            print("[DEBUG] Launching browser...")
            launch_options = {
                'headless': self.config['browser']['headless']
            }
            if 'slowMo' in self.config['browser']:
                launch_options['slow_mo'] = self.config['browser']['slowMo']
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            print("[DEBUG] Creating context...")
            self.context = await self.browser.new_context(
                viewport=self.config['browser']['viewport']
            )
            print("[DEBUG] Creating page...")
            self.page = await self.context.new_page()
            
            # CRITICAL: Update class-level shared instances IMMEDIATELY
            BrowserTester._shared_browser = self.browser
            BrowserTester._shared_context = self.context
            BrowserTester._shared_page = self.page
            BrowserTester._shared_playwright = self.playwright
            
            print(f"[DEBUG] Shared state updated: browser={BrowserTester._shared_browser is not None}, page={BrowserTester._shared_page is not None}")
            
            # Capture console logs
            self.page.on('console', lambda msg: self.console_logs.append({
                'type': msg.type,
                'text': msg.text,
                'timestamp': datetime.now().isoformat()
            }))
            
            # Capture errors
            self.page.on('pageerror', lambda err: self.console_logs.append({
                'type': 'error',
                'text': str(err),
                'timestamp': datetime.now().isoformat()
            }))
            
            return {"status": "initialized", "message": "Browser ready"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            # Auto-initialize if browser not ready
            if not self.page or not self.browser or not self.context:
                print("Browser not initialized, initializing now...")
                init_result = await self.initialize()
                if init_result.get("status") == "error":
                    return init_result
            
            # Sync instance variables from shared state
            self.browser = BrowserTester._shared_browser
            self.context = BrowserTester._shared_context
            self.page = BrowserTester._shared_page
            self.playwright = BrowserTester._shared_playwright
            
            # Double check page is valid
            if not self.page:
                return {"status": "error", "message": "Failed to initialize browser page"}
            
            self.console_logs = []  # Clear previous logs
            
            # Debug logging to file
            with open("C:/Users/ggfuc/mcp_browser_debug.log", "a") as f:
                f.write(f"\n[DEBUG] About to navigate to {url}\n")
                f.write(f"[DEBUG] Before goto - page valid: {self.page is not None}\n")
                f.write(f"[DEBUG] Before goto - browser valid: {self.browser is not None}\n")
            
            response = await self.page.goto(url, timeout=self.config['browser']['timeout'], wait_until='networkidle')
            
            # Wait a moment for page to stabilize
            await asyncio.sleep(0.5)
            
            # CRITICAL: Update shared state IMMEDIATELY after goto, before anything else!
            BrowserTester._shared_browser = self.browser
            BrowserTester._shared_context = self.context
            BrowserTester._shared_page = self.page
            BrowserTester._shared_playwright = self.playwright
            
            print(f"[DEBUG] After goto - shared updated: browser={BrowserTester._shared_browser is not None}, page={BrowserTester._shared_page is not None}")
            print(f"[DEBUG] Page is closed? {self.page.is_closed()}")
            
            title = await self.page.title()
            
            print(f"[DEBUG] Got title, about to return...")
            
            return {
                "status": "success",
                "url": url,
                "status_code": response.status if response else None,
                "title": title
            }
        except Exception as e:
            # If navigation fails, try reinitializing
            try:
                print(f"Navigation error: {e}, attempting to reinitialize...")
                await self.initialize()
                # Sync instance variables again after reinit
                self.browser = BrowserTester._shared_browser
                self.context = BrowserTester._shared_context
                self.page = BrowserTester._shared_page
                self.playwright = BrowserTester._shared_playwright
                
                response = await self.page.goto(url, timeout=self.config['browser']['timeout'])
                return {
                    "status": "success",
                    "url": url,
                    "status_code": response.status if response else None,
                    "title": await self.page.title()
                }
            except Exception as e2:
                return {"status": "error", "message": f"Navigation failed: {str(e2)}"}
    
    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element by CSS selector."""
        # Sync instance variables from shared state
        self.browser = BrowserTester._shared_browser
        self.context = BrowserTester._shared_context
        self.page = BrowserTester._shared_page
        self.playwright = BrowserTester._shared_playwright
        
        # Debug logging
        print(f"[DEBUG] click_element called. browser={self.browser is not None}, page={self.page is not None}")
        
        if not self.page or not self.browser:
            return {
                "status": "error", 
                "message": f"Browser not ready - browser={self.browser is not None}, page={self.page is not None}"
            }
        
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            return {"status": "success", "selector": selector}
        except Exception as e:
            return {"status": "error", "message": f"Click failed: {str(e)}", "selector": selector}
    
    async def fill_input(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill an input field."""
        # Sync instance variables from shared state
        self.browser = BrowserTester._shared_browser
        self.context = BrowserTester._shared_context
        self.page = BrowserTester._shared_page
        self.playwright = BrowserTester._shared_playwright
        
        if not self.page or not self.browser:
            return {"status": "error", "message": "Browser not ready - call browser_navigate or browser_restart first"}
        
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.fill(selector, value)
            return {"status": "success", "selector": selector}
        except Exception as e:
            return {"status": "error", "message": str(e), "selector": selector}
    
    async def get_screenshot(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Capture a screenshot."""
        # Sync instance variables from shared state
        self.browser = BrowserTester._shared_browser
        self.context = BrowserTester._shared_context
        self.page = BrowserTester._shared_page
        self.playwright = BrowserTester._shared_playwright
        
        # Debug logging
        print(f"[DEBUG] get_screenshot called. browser={self.browser is not None}, page={self.page is not None}")
        
        if not self.page or not self.browser:
            return {
                "status": "error", 
                "message": f"Browser not ready - browser={self.browser is not None}, page={self.page is not None}"
            }
        
        try:
            if not name:
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            filepath = self.screenshots_dir / f"{name}.{self.config['screenshots']['format']}"
            await self.page.screenshot(path=str(filepath), full_page=True)
            
            return {
                "status": "success",
                "path": str(filepath),
                "name": name
            }
        except Exception as e:
            return {"status": "error", "message": f"Screenshot failed: {str(e)}"}
    
    async def get_console_errors(self) -> Dict[str, Any]:
        """Get console logs and errors."""
        errors = [log for log in self.console_logs if log['type'] == 'error']
        warnings = [log for log in self.console_logs if log['type'] == 'warning']
        
        return {
            "errors": errors,
            "warnings": warnings,
            "all_logs": self.console_logs
        }
    
    async def evaluate_js(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript in the page."""
        # Sync instance variables from shared state
        self.browser = BrowserTester._shared_browser
        self.context = BrowserTester._shared_context
        self.page = BrowserTester._shared_page
        self.playwright = BrowserTester._shared_playwright
        
        if not self.page or not self.browser:
            return {"status": "error", "message": "Browser not ready - call browser_navigate or browser_restart first"}
        
        try:
            result = await self.page.evaluate(script)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()
        
        # Reset instance state
        self.browser = None
        self.context = None
        self.page = None
        self.console_logs = []
        
        # Reset shared state
        BrowserTester._shared_browser = None
        BrowserTester._shared_context = None
        BrowserTester._shared_page = None
        BrowserTester._shared_playwright = None
        
        return {"status": "closed"}
    
    async def restart(self):
        """Restart the browser (close and reinitialize)."""
        print("[DEBUG] restart() called")
        try:
            # Close existing browser
            if self.browser:
                print("[DEBUG] Closing existing browser...")
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                print("[DEBUG] Stopping playwright...")
                await self.playwright.stop()
            
            # Reset instance state
            print("[DEBUG] Resetting state to None...")
            self.browser = None
            self.context = None
            self.page = None
            self.console_logs = []
            
            # Reset shared state
            BrowserTester._shared_browser = None
            BrowserTester._shared_context = None
            BrowserTester._shared_page = None
            BrowserTester._shared_playwright = None
            
            # Reinitialize
            print("[DEBUG] Calling initialize()...")
            result = await self.initialize()
            print(f"[DEBUG] Initialize returned: {result}")
            print(f"[DEBUG] After init: browser={self.browser is not None}, page={self.page is not None}")
            return result
        except Exception as e:
            print(f"[DEBUG] restart() error: {e}")
            return {"status": "error", "message": str(e)}
