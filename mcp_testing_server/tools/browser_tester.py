"""Browser automation tools using Patchright for undetectable testing."""
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class BrowserTester:
    """Controls browser for testing websites and web apps."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser = None
        self.context = None
        self.page = None
        self.console_logs = []
        self.screenshots_dir = Path(config['screenshots']['path'])
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize Patchright browser."""
        try:
            from patchright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config['browser']['headless']
            )
            self.context = await self.browser.new_context(
                viewport=self.config['browser']['viewport']
            )
            self.page = await self.context.new_page()
            
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
        if not self.page:
            await self.initialize()
        
        try:
            self.console_logs = []  # Clear previous logs
            response = await self.page.goto(url, timeout=self.config['browser']['timeout'])
            
            return {
                "status": "success",
                "url": url,
                "status_code": response.status if response else None,
                "title": await self.page.title()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element by CSS selector."""
        if not self.page:
            return {"status": "error", "message": "Browser not initialized"}
        
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            return {"status": "success", "selector": selector}
        except Exception as e:
            return {"status": "error", "message": str(e), "selector": selector}
    
    async def fill_input(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill an input field."""
        if not self.page:
            return {"status": "error", "message": "Browser not initialized"}
        
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.fill(selector, value)
            return {"status": "success", "selector": selector}
        except Exception as e:
            return {"status": "error", "message": str(e), "selector": selector}
    
    async def get_screenshot(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Capture a screenshot."""
        if not self.page:
            return {"status": "error", "message": "Browser not initialized"}
        
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
            return {"status": "error", "message": str(e)}
    
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
        if not self.page:
            return {"status": "error", "message": "Browser not initialized"}
        
        try:
            result = await self.page.evaluate(script)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        # Reset state
        self.browser = None
        self.context = None
        self.page = None
        self.console_logs = []
        
        return {"status": "closed"}
    
    async def restart(self):
        """Restart the browser (close and reinitialize)."""
        try:
            # Close existing browser
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
            
            # Reset state
            self.browser = None
            self.context = None
            self.page = None
            self.console_logs = []
            
            # Reinitialize
            return await self.initialize()
        except Exception as e:
            return {"status": "error", "message": str(e)}
