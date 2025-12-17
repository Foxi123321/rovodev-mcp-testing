"""
Rex Task Orchestrator - Visual Testing Suite
Browser automation → Screenshot → Llava analysis → Validation
"""
import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VisualTestResult:
    test_id: str
    url: str
    expected_description: str
    screenshot_path: str
    llava_analysis: str
    passed: bool
    confidence: float
    timestamp: float
    duration: float
    errors: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "url": self.url,
            "expected_description": self.expected_description,
            "screenshot_path": self.screenshot_path,
            "llava_analysis": self.llava_analysis,
            "passed": self.passed,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "errors": self.errors
        }


class VisualTester:
    """
    Visual testing system that:
    1. Launches app in browser
    2. Takes screenshot
    3. Analyzes with llava
    4. Compares to expected behavior
    5. Tests interactive elements
    """
    
    def __init__(self, config: Dict, mcp_clients: Dict):
        self.config = config
        self.screenshot_dir = config.get("screenshot_dir", "screenshots")
        self.confidence_threshold = config.get("analysis_confidence_threshold", 0.7)
        self.auto_retry = config.get("auto_retry_on_mismatch", True)
        self.max_retries = config.get("max_visual_retries", 2)
        
        # MCP client references (passed from main server)
        self.browser_client = mcp_clients.get("testing_review_server")
        self.vision_client = mcp_clients.get("vision_server_simple")
        
        self.test_history: List[VisualTestResult] = []
        
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    async def run_visual_test(
        self,
        url: str,
        expected_description: str,
        test_id: Optional[str] = None,
        elements_to_test: Optional[List[Dict]] = None
    ) -> VisualTestResult:
        """
        Run complete visual test:
        1. Navigate to URL
        2. Screenshot
        3. Llava analysis
        4. Compare to expected
        5. Test interactive elements
        """
        start_time = time.time()
        test_id = test_id or f"visual_test_{int(start_time)}"
        errors = []
        
        logger.info(f"Starting visual test: {test_id} for {url}")
        
        try:
            # Step 1: Navigate to URL
            logger.info(f"Navigating to {url}")
            nav_result = await self._call_browser("browser_navigate", {"url": url})
            
            if nav_result.get("status") != "success":
                errors.append(f"Navigation failed: {nav_result}")
                raise Exception("Navigation failed")
            
            # Wait for page to settle
            await self._call_browser("browser_execute_js", {
                "script": "return new Promise(resolve => setTimeout(resolve, 2000))"
            })
            
            # Step 2: Take screenshot
            logger.info("Taking screenshot")
            screenshot_name = f"{test_id}_{int(time.time())}"
            screenshot_result = await self._call_browser("browser_screenshot", {
                "name": screenshot_name
            })
            
            if screenshot_result.get("status") != "success":
                errors.append(f"Screenshot failed: {screenshot_result}")
                raise Exception("Screenshot failed")
            
            screenshot_path = screenshot_result.get("path", f"{self.screenshot_dir}/{screenshot_name}.png")
            
            # Step 3: Analyze with llava
            logger.info("Analyzing screenshot with llava")
            analysis_prompt = f"""Analyze this screenshot and determine if it matches this description:
Expected: {expected_description}

Provide:
1. What you see in the screenshot
2. Whether it matches the expected description (YES/NO)
3. Confidence level (0-1)
4. Any discrepancies or issues"""
            
            vision_result = await self._call_vision("analyze_image", {
                "image_path": screenshot_path,
                "prompt": analysis_prompt,
                "wait": True
            })
            
            llava_analysis = vision_result if isinstance(vision_result, str) else str(vision_result)
            
            # Step 4: Parse analysis and determine pass/fail
            passed, confidence = self._parse_analysis(llava_analysis, expected_description)
            
            logger.info(f"Visual test result: {'PASS' if passed else 'FAIL'} (confidence: {confidence:.2f})")
            
            # Step 5: Test interactive elements if provided
            if elements_to_test and passed:
                element_results = await self._test_elements(elements_to_test)
                if not all(element_results.values()):
                    passed = False
                    errors.append(f"Interactive element tests failed: {element_results}")
            
        except Exception as e:
            logger.error(f"Visual test error: {e}")
            errors.append(str(e))
            passed = False
            confidence = 0.0
            llava_analysis = f"Test failed: {e}"
            screenshot_path = ""
        
        duration = time.time() - start_time
        
        result = VisualTestResult(
            test_id=test_id,
            url=url,
            expected_description=expected_description,
            screenshot_path=screenshot_path,
            llava_analysis=llava_analysis,
            passed=passed,
            confidence=confidence,
            timestamp=start_time,
            duration=duration,
            errors=errors
        )
        
        self.test_history.append(result)
        
        # Auto-retry logic
        if not passed and self.auto_retry and result.confidence < self.confidence_threshold:
            retry_count = getattr(self, '_retry_count', 0)
            if retry_count < self.max_retries:
                self._retry_count = retry_count + 1
                logger.info(f"Retrying visual test (attempt {self._retry_count + 1}/{self.max_retries})")
                time.sleep(2)  # Wait before retry
                return await self.run_visual_test(url, expected_description, test_id, elements_to_test)
        
        self._retry_count = 0  # Reset counter
        return result
    
    async def _test_elements(self, elements: List[Dict]) -> Dict[str, bool]:
        """Test interactive elements (buttons, links, inputs)"""
        results = {}
        
        for element in elements:
            element_type = element.get("type")  # "button", "link", "input"
            selector = element.get("selector")
            action = element.get("action")  # "click", "fill", etc
            expected_result = element.get("expected")
            
            try:
                if action == "click":
                    await self._call_browser("browser_click", {"selector": selector})
                    results[selector] = True
                elif action == "fill":
                    value = element.get("value", "")
                    await self._call_browser("browser_fill", {"selector": selector, "value": value})
                    results[selector] = True
                else:
                    results[selector] = False
                    
            except Exception as e:
                logger.error(f"Element test failed for {selector}: {e}")
                results[selector] = False
        
        return results
    
    def _parse_analysis(self, analysis: str, expected: str) -> tuple[bool, float]:
        """Parse llava analysis to determine pass/fail and confidence"""
        analysis_lower = analysis.lower()
        
        # Look for explicit YES/NO
        if "yes" in analysis_lower and "matches" in analysis_lower:
            passed = True
            confidence = 0.8
        elif "no" in analysis_lower and "does not match" in analysis_lower:
            passed = False
            confidence = 0.8
        else:
            # Fuzzy matching - check if key terms from expected are in analysis
            expected_terms = expected.lower().split()
            matches = sum(1 for term in expected_terms if term in analysis_lower)
            confidence = matches / len(expected_terms) if expected_terms else 0
            passed = confidence >= self.confidence_threshold
        
        # Look for explicit confidence value
        if "confidence" in analysis_lower:
            try:
                # Extract number after "confidence"
                parts = analysis_lower.split("confidence")
                if len(parts) > 1:
                    numbers = [float(s) for s in parts[1].split() if s.replace('.','').isdigit()]
                    if numbers:
                        confidence = min(numbers[0], 1.0)
            except:
                pass
        
        return passed, confidence
    
    async def _call_browser(self, tool_name: str, tool_input: Dict) -> Any:
        """Call browser MCP tool"""
        # This will be replaced with actual MCP client call
        # For now, return mock structure
        logger.info(f"Browser call: {tool_name} with {tool_input}")
        return {"status": "success", "message": "Mock browser call"}
    
    async def _call_vision(self, tool_name: str, tool_input: Dict) -> Any:
        """Call vision MCP tool"""
        # This will be replaced with actual MCP client call
        logger.info(f"Vision call: {tool_name} with {tool_input}")
        return "Mock vision analysis"
    
    def get_test_history(self, last_n: int = 10) -> List[Dict]:
        """Get recent test history"""
        return [t.to_dict() for t in self.test_history[-last_n:]]
    
    def get_test_result(self, test_id: str) -> Optional[Dict]:
        """Get specific test result"""
        for test in self.test_history:
            if test.test_id == test_id:
                return test.to_dict()
        return None
    
    def get_test_stats(self) -> Dict:
        """Get overall test statistics"""
        if not self.test_history:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "avg_confidence": 0.0,
                "avg_duration": 0.0
            }
        
        total = len(self.test_history)
        passed = sum(1 for t in self.test_history if t.passed)
        failed = total - passed
        pass_rate = passed / total if total > 0 else 0
        avg_confidence = sum(t.confidence for t in self.test_history) / total
        avg_duration = sum(t.duration for t in self.test_history) / total
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_confidence": avg_confidence,
            "avg_duration": avg_duration
        }
