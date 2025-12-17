"""Decision system for adaptive exploration strategy."""

from typing import Dict, Any, Optional, List
import random


class DecisionSystem:
    """Makes intelligent decisions about exploration strategy."""
    
    def __init__(self):
        """Initialize decision system."""
        self.decision_history = []
    
    def decide_next_action(
        self,
        current_state: Dict[str, Any],
        goal: Dict[str, Any],
        past_attempts: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Decide what action to take next.
        
        Args:
            current_state: Current website state
            goal: Exploration goal
            past_attempts: History of past attempts
            
        Returns:
            Decision with action and reasoning
        """
        # RULE 1: If past learning has high success rate, use it
        if past_attempts:
            success_rate = self._calculate_success_rate(past_attempts)
            if success_rate > 0.7:
                return {
                    "action": "repeat_successful_pattern",
                    "reasoning": f"Past success rate: {success_rate:.1%}",
                    "strategy": "exploit"
                }
        
        # RULE 2: If confidence is low, explore more
        confidence = current_state.get("confidence", {}).get("overall", 0.0)
        if confidence < 0.5:
            return {
                "action": "explore_more",
                "reasoning": f"Low confidence: {confidence:.1%}",
                "strategy": "explore"
            }
        
        # RULE 3: If goal requires data and APIs are available, prefer API
        if goal.get("goal_type") == "data_extraction":
            api_endpoints = current_state.get("capabilities", {}).get("api_endpoints", [])
            if len(api_endpoints) > 0:
                return {
                    "action": "use_api",
                    "reasoning": f"Found {len(api_endpoints)} API endpoints",
                    "strategy": "api_first"
                }
        
        # RULE 4: Default to UI interaction
        return {
            "action": "use_ui",
            "reasoning": "Default strategy - direct UI interaction",
            "strategy": "ui_first"
        }
    
    def _calculate_success_rate(self, attempts: List[Dict[str, Any]]) -> float:
        """Calculate success rate from past attempts."""
        if not attempts:
            return 0.0
        
        successes = sum(1 for a in attempts if a.get("success", False))
        return successes / len(attempts)
    
    def should_pivot_strategy(
        self,
        current_strategy: str,
        success_count: int,
        failure_count: int,
        confidence: float
    ) -> bool:
        """Decide if strategy should be pivoted.
        
        Args:
            current_strategy: Current exploration strategy
            success_count: Number of successes
            failure_count: Number of failures
            confidence: Current confidence level
            
        Returns:
            True if strategy should pivot
        """
        # Pivot if too many failures
        if failure_count >= 3:
            return True
        
        # Pivot if success rate is low
        total = success_count + failure_count
        if total >= 5:
            success_rate = success_count / total
            if success_rate < 0.4:
                return True
        
        # Pivot if confidence is declining
        if confidence < 0.3:
            return True
        
        return False
    
    def select_pivot_strategy(
        self,
        current_strategy: str,
        available_strategies: List[str]
    ) -> str:
        """Select a new strategy to pivot to.
        
        Args:
            current_strategy: Current strategy
            available_strategies: List of available strategies
            
        Returns:
            New strategy to try
        """
        # Remove current strategy from options
        options = [s for s in available_strategies if s != current_strategy]
        
        if not options:
            return current_strategy
        
        # Prioritize API if available
        if "api_first" in options:
            return "api_first"
        
        # Otherwise pick randomly
        return random.choice(options)
    
    def evaluate_goal_progress(
        self,
        goal: Dict[str, Any],
        current_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate progress toward goal.
        
        Args:
            goal: The exploration goal
            current_result: Current exploration result
            
        Returns:
            Progress evaluation
        """
        success_criteria = goal.get("success_criteria", {})
        must_have = success_criteria.get("must_have", [])
        quality_threshold = success_criteria.get("quality_threshold", 0.7)
        
        # Check must-have criteria
        must_have_met = 0
        for criterion in must_have:
            if self._check_criterion(criterion, current_result):
                must_have_met += 1
        
        must_have_score = must_have_met / len(must_have) if must_have else 0.0
        
        # Overall progress
        progress = {
            "must_have_score": must_have_score,
            "quality_score": current_result.get("quality", 0.0),
            "meets_threshold": must_have_score >= quality_threshold,
            "complete": must_have_score >= quality_threshold and must_have_met == len(must_have)
        }
        
        return progress
    
    def _check_criterion(self, criterion: str, result: Dict[str, Any]) -> bool:
        """Check if a success criterion is met.
        
        Args:
            criterion: The criterion to check
            result: Current result
            
        Returns:
            True if criterion is met
        """
        # Simple keyword matching for now
        # In real implementation, would be more sophisticated
        criterion_lower = criterion.lower()
        result_str = str(result).lower()
        
        return criterion_lower in result_str
