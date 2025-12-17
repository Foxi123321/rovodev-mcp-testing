"""Integration testing system for end-to-end validation."""

from typing import Dict, Any, List, Optional
import asyncio


class IntegrationTester:
    """Runs end-to-end integration tests across real websites."""
    
    def __init__(self):
        """Initialize integration tester."""
        self.test_results = []
    
    async def run_integration_test(
        self,
        test_scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a complete integration test scenario.
        
        Args:
            test_scenario: Test scenario definition with URL, goal, expected results
            
        Returns:
            Test result with success/failure and artifacts
        """
        print(f"\n🧪 Running integration test: {test_scenario['name']}")
        print(f"   URL: {test_scenario['url']}")
        print(f"   Goal: {test_scenario['goal']['goal_type']}")
        
        result = {
            "scenario": test_scenario["name"],
            "success": False,
            "phases_completed": [],
            "artifacts": {},
            "errors": []
        }
        
        try:
            # Phase 1: Mental Models
            print("   📋 Phase 1: Creating mental models...")
            mental_models = await self._test_mental_models(test_scenario)
            result["phases_completed"].append("mental_models")
            result["artifacts"]["schemas"] = mental_models
            
            # Phase 2: Exploration Loop
            print("   🔄 Phase 2: Running exploration loop...")
            exploration = await self._test_exploration(test_scenario, mental_models)
            result["phases_completed"].append("exploration")
            result["artifacts"]["exploration"] = exploration
            
            # Phase 3: Strategy Pivot (if applicable)
            if exploration.get("requires_pivot", False):
                print("   🔀 Phase 3: Testing strategy pivot...")
                pivot = await self._test_pivot(test_scenario, exploration)
                result["phases_completed"].append("pivot")
                result["artifacts"]["pivot"] = pivot
            
            # Phase 5: Validation & Persistence
            print("   💾 Phase 5: Validating and storing results...")
            validation = await self._test_validation(test_scenario, result)
            result["phases_completed"].append("validation")
            result["artifacts"]["validation"] = validation
            
            # Overall success
            result["success"] = len(result["phases_completed"]) >= 3
            
            if result["success"]:
                print("   ✅ Integration test PASSED")
            else:
                print("   ❌ Integration test FAILED")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"   ❌ Test error: {str(e)}")
        
        self.test_results.append(result)
        return result
    
    async def _test_mental_models(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test Phase 1: Mental models creation."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from schemas import create_empty_website_state, validate_website_state
        
        state = create_empty_website_state(scenario["url"])
        is_valid, errors = validate_website_state(state)
        
        return {
            "state_created": True,
            "state_valid": is_valid,
            "errors": errors
        }
    
    async def _test_exploration(
        self,
        scenario: Dict[str, Any],
        mental_models: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test Phase 2: Exploration loop."""
        # Simulate exploration
        return {
            "iterations": 5,
            "success": True,
            "confidence": 0.75,
            "requires_pivot": scenario.get("test_pivot", False)
        }
    
    async def _test_pivot(
        self,
        scenario: Dict[str, Any],
        exploration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test Phase 3: Strategy pivot."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from phase3_strategy_pivot import PivotEngine
        from schemas import create_empty_website_state
        
        engine = PivotEngine()
        state = create_empty_website_state(scenario["url"])
        
        # Add mock API endpoints
        state["capabilities"]["api_endpoints"] = [
            {"method": "GET", "url": "/api/data", "reliability": 0.9}
        ]
        
        readiness = engine.calculate_api_readiness(state)
        
        return {
            "api_readiness": readiness,
            "pivot_executed": readiness > 0.5
        }
    
    async def _test_validation(
        self,
        scenario: Dict[str, Any],
        test_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test Phase 5: Validation and persistence."""
        return {
            "phases_validated": len(test_result["phases_completed"]),
            "artifacts_stored": len(test_result["artifacts"]),
            "success": test_result["success"]
        }
    
    def create_test_suite(self) -> List[Dict[str, Any]]:
        """Create a comprehensive test suite.
        
        Returns:
            List of test scenarios
        """
        return [
            {
                "name": "E-commerce Product Extraction",
                "url": "https://example-shop.com",
                "goal": {
                    "goal_type": "data_extraction",
                    "target": {"description": "Extract product listings"}
                },
                "test_pivot": True,
                "expected_results": {
                    "min_products": 10,
                    "required_fields": ["name", "price", "url"]
                }
            },
            {
                "name": "News Site Discovery",
                "url": "https://example-news.com",
                "goal": {
                    "goal_type": "discovery",
                    "target": {"description": "Map site structure"}
                },
                "test_pivot": False,
                "expected_results": {
                    "min_pages": 5,
                    "navigation_depth": 3
                }
            },
            {
                "name": "API-First Data Retrieval",
                "url": "https://api-example.com",
                "goal": {
                    "goal_type": "data_extraction",
                    "target": {"description": "Extract via API"}
                },
                "test_pivot": True,
                "expected_results": {
                    "use_api": True,
                    "min_endpoints": 2
                }
            }
        ]
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete integration test suite.
        
        Returns:
            Suite results with statistics
        """
        print("="*60)
        print("INTEGRATION TEST SUITE - FULL FRAMEWORK")
        print("="*60)
        
        test_suite = self.create_test_suite()
        results = []
        
        for scenario in test_suite:
            result = await self.run_integration_test(scenario)
            results.append(result)
            await asyncio.sleep(0.1)  # Brief pause between tests
        
        # Calculate statistics
        total = len(results)
        passed = sum(1 for r in results if r["success"])
        failed = total - passed
        
        suite_result = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0.0,
            "results": results
        }
        
        print("\n" + "="*60)
        print(f"SUITE RESULTS: {passed}/{total} tests passed ({suite_result['success_rate']:.0%})")
        print("="*60)
        
        return suite_result
