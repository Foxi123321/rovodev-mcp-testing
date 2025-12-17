"""Strategy pivot engine - Intelligently switches between UI and API strategies."""

from typing import Dict, Any, List, Optional


class PivotEngine:
    """Manages intelligent pivoting between exploration strategies."""
    
    def __init__(self):
        """Initialize pivot engine."""
        self.pivot_history = []
        self.api_reliability_threshold = 0.7
        self.ui_fallback_threshold = 0.4
    
    def calculate_api_readiness(self, website_state: Dict[str, Any]) -> float:
        """Calculate how ready the website is for API-based extraction.
        
        Args:
            website_state: Current website state
            
        Returns:
            API readiness score (0-1)
        """
        api_endpoints = website_state.get("capabilities", {}).get("api_endpoints", [])
        
        if not api_endpoints:
            return 0.0
        
        # Factors contributing to API readiness
        factors = []
        
        # 1. Number of discovered endpoints (max score at 5+ endpoints)
        endpoint_score = min(1.0, len(api_endpoints) / 5.0)
        factors.append(("endpoint_count", endpoint_score, 0.3))
        
        # 2. Average reliability of endpoints
        reliabilities = [ep.get("reliability", 0.5) for ep in api_endpoints]
        avg_reliability = sum(reliabilities) / len(reliabilities) if reliabilities else 0.0
        factors.append(("reliability", avg_reliability, 0.4))
        
        # 3. Endpoint diversity (different methods)
        methods = set(ep.get("method", "GET") for ep in api_endpoints)
        diversity_score = min(1.0, len(methods) / 3.0)  # Max score at 3+ methods
        factors.append(("diversity", diversity_score, 0.2))
        
        # 4. Response schema quality
        schemas = [ep for ep in api_endpoints if ep.get("response_schema")]
        schema_score = len(schemas) / len(api_endpoints) if api_endpoints else 0.0
        factors.append(("schema_quality", schema_score, 0.1))
        
        # Weighted sum
        api_readiness = sum(score * weight for _, score, weight in factors)
        
        return api_readiness
    
    def should_pivot_to_api(
        self,
        current_strategy: str,
        website_state: Dict[str, Any],
        ui_success_rate: float
    ) -> Dict[str, Any]:
        """Decide if should pivot from UI to API strategy.
        
        Args:
            current_strategy: Current exploration strategy
            website_state: Current website state
            ui_success_rate: Success rate of UI strategy
            
        Returns:
            Pivot decision with reasoning
        """
        if current_strategy == "api_first":
            return {
                "should_pivot": False,
                "reason": "Already using API strategy"
            }
        
        api_readiness = self.calculate_api_readiness(website_state)
        
        # Pivot if API is ready and UI is struggling
        if api_readiness >= self.api_reliability_threshold and ui_success_rate < 0.5:
            return {
                "should_pivot": True,
                "to_strategy": "api_first",
                "reason": f"API readiness: {api_readiness:.0%}, UI success: {ui_success_rate:.0%}",
                "confidence": api_readiness
            }
        
        # Pivot if API is highly ready regardless of UI performance
        if api_readiness >= 0.9:
            return {
                "should_pivot": True,
                "to_strategy": "api_first",
                "reason": f"High API readiness: {api_readiness:.0%}",
                "confidence": api_readiness
            }
        
        return {
            "should_pivot": False,
            "reason": f"API not ready enough ({api_readiness:.0%})"
        }
    
    def should_rollback_to_ui(
        self,
        current_strategy: str,
        api_success_rate: float,
        api_failures: int
    ) -> Dict[str, Any]:
        """Decide if should rollback from API to UI strategy.
        
        Args:
            current_strategy: Current strategy
            api_success_rate: Success rate of API attempts
            api_failures: Number of consecutive API failures
            
        Returns:
            Rollback decision with reasoning
        """
        if current_strategy != "api_first":
            return {
                "should_rollback": False,
                "reason": "Not using API strategy"
            }
        
        # Rollback if too many failures
        if api_failures >= 3:
            return {
                "should_rollback": True,
                "to_strategy": "ui_first",
                "reason": f"{api_failures} consecutive API failures",
                "confidence": 0.9
            }
        
        # Rollback if success rate is too low
        if api_success_rate < self.ui_fallback_threshold:
            return {
                "should_rollback": True,
                "to_strategy": "ui_first",
                "reason": f"Low API success rate: {api_success_rate:.0%}",
                "confidence": 0.7
            }
        
        return {
            "should_rollback": False,
            "reason": f"API performing adequately ({api_success_rate:.0%})"
        }
    
    async def execute_pivot(
        self,
        from_strategy: str,
        to_strategy: str,
        website_state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a strategy pivot with validation.
        
        Args:
            from_strategy: Current strategy
            to_strategy: Target strategy
            website_state: Current website state
            goal: Exploration goal
            
        Returns:
            Pivot execution result
        """
        print(f"🔀 Pivoting: {from_strategy} → {to_strategy}")
        
        pivot_record = {
            "from": from_strategy,
            "to": to_strategy,
            "timestamp": self._get_timestamp(),
            "reason": f"Strategic pivot to {to_strategy}",
            "success": False
        }
        
        try:
            # Pre-pivot validation
            validation = await self._validate_pivot(to_strategy, website_state)
            
            if not validation["valid"]:
                pivot_record["error"] = validation["reason"]
                self.pivot_history.append(pivot_record)
                return {
                    "success": False,
                    "error": validation["reason"]
                }
            
            # Execute pivot
            if to_strategy == "api_first":
                result = await self._pivot_to_api(website_state, goal)
            elif to_strategy == "ui_first":
                result = await self._pivot_to_ui(website_state, goal)
            else:
                result = {"success": False, "error": f"Unknown strategy: {to_strategy}"}
            
            pivot_record["success"] = result.get("success", False)
            pivot_record["result"] = result
            
            self.pivot_history.append(pivot_record)
            
            return result
            
        except Exception as e:
            pivot_record["error"] = str(e)
            self.pivot_history.append(pivot_record)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_pivot(
        self,
        to_strategy: str,
        website_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if pivot is possible.
        
        Args:
            to_strategy: Target strategy
            website_state: Current website state
            
        Returns:
            Validation result
        """
        if to_strategy == "api_first":
            api_endpoints = website_state.get("capabilities", {}).get("api_endpoints", [])
            if not api_endpoints:
                return {
                    "valid": False,
                    "reason": "No API endpoints available for API strategy"
                }
            
            api_readiness = self.calculate_api_readiness(website_state)
            if api_readiness < 0.3:
                return {
                    "valid": False,
                    "reason": f"API readiness too low: {api_readiness:.0%}"
                }
        
        elif to_strategy == "ui_first":
            ui_interactions = website_state.get("capabilities", {}).get("ui_interactions", [])
            if not ui_interactions:
                return {
                    "valid": False,
                    "reason": "No UI interactions available"
                }
        
        return {"valid": True}
    
    async def _pivot_to_api(
        self,
        website_state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute pivot to API strategy."""
        api_endpoints = website_state.get("capabilities", {}).get("api_endpoints", [])
        
        # Would use api-testing MCP to record/replay API calls
        return {
            "success": True,
            "strategy": "api_first",
            "endpoints_available": len(api_endpoints),
            "message": f"Pivoted to API strategy with {len(api_endpoints)} endpoints"
        }
    
    async def _pivot_to_ui(
        self,
        website_state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute rollback to UI strategy."""
        ui_interactions = website_state.get("capabilities", {}).get("ui_interactions", [])
        
        # Would use browser automation for UI interactions
        return {
            "success": True,
            "strategy": "ui_first",
            "interactions_available": len(ui_interactions),
            "message": f"Rolled back to UI strategy with {len(ui_interactions)} interactions"
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def get_pivot_statistics(self) -> Dict[str, Any]:
        """Get statistics about pivots."""
        if not self.pivot_history:
            return {"no_data": True}
        
        total_pivots = len(self.pivot_history)
        successful = sum(1 for p in self.pivot_history if p["success"])
        
        pivot_types = {}
        for pivot in self.pivot_history:
            key = f"{pivot['from']}→{pivot['to']}"
            pivot_types[key] = pivot_types.get(key, 0) + 1
        
        return {
            "total_pivots": total_pivots,
            "successful": successful,
            "failed": total_pivots - successful,
            "success_rate": successful / total_pivots if total_pivots > 0 else 0.0,
            "pivot_types": pivot_types
        }
