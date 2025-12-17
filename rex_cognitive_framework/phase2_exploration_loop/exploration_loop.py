"""Core exploration loop - The cognitive engine for website intelligence.

This implements the OBSERVE → DECIDE → ACT → LEARN cycle.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from .perception import PerceptionSystem
from .decision import DecisionSystem


class ExplorationLoop:
    """Core cognitive loop for website exploration."""
    
    def __init__(self):
        """Initialize the exploration loop."""
        self.perception = PerceptionSystem()
        self.decision = DecisionSystem()
        self.loop_history = []
        self.max_iterations = 10
        self.timeout_seconds = 300  # 5 minutes
    
    async def explore(
        self,
        url: str,
        goal: Dict[str, Any],
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute full exploration loop toward a goal.
        
        Args:
            url: Website URL to explore
            goal: Exploration goal (from goal schema)
            initial_state: Optional initial website state
            
        Returns:
            Exploration result with learned state
        """
        print(f"🔥 Starting exploration of {url}")
        print(f"🎯 Goal: {goal['goal_type']} - {goal['target']['description']}")
        
        # Initialize state
        current_state = initial_state or self._create_initial_state(url)
        iterations = 0
        start_time = datetime.utcnow()
        
        exploration_result = {
            "success": False,
            "iterations": 0,
            "final_state": None,
            "learned_patterns": [],
            "error": None
        }
        
        try:
            while iterations < self.max_iterations:
                iterations += 1
                print(f"\n🔄 Iteration {iterations}/{self.max_iterations}")
                
                # Check timeout
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if elapsed > self.timeout_seconds:
                    print(f"⏱️  Timeout after {elapsed:.1f}s")
                    break
                
                # PHASE 1: OBSERVE
                print("  👁️  OBSERVE: Perceiving website...")
                perceptions = await self.perception.perceive(url)
                current_state = self.perception.fuse_perceptions(perceptions)
                
                # PHASE 2: DECIDE
                print("  🧠 DECIDE: Choosing next action...")
                decision = self.decision.decide_next_action(
                    current_state,
                    goal,
                    self.loop_history
                )
                print(f"     Strategy: {decision['strategy']}")
                print(f"     Reasoning: {decision['reasoning']}")
                
                # PHASE 3: ACT
                print("  ⚡ ACT: Executing action...")
                action_result = await self._execute_action(
                    decision,
                    current_state,
                    goal
                )
                
                # PHASE 4: LEARN
                print("  📚 LEARN: Updating knowledge...")
                learned = self._learn_from_result(
                    decision,
                    action_result,
                    current_state
                )
                
                # Store iteration
                self.loop_history.append({
                    "iteration": iterations,
                    "decision": decision,
                    "result": action_result,
                    "learned": learned,
                    "state": current_state
                })
                
                # Check if goal achieved
                progress = self.decision.evaluate_goal_progress(goal, action_result)
                print(f"  📊 Progress: {progress['must_have_score']:.0%}")
                
                if progress["complete"]:
                    print("  ✅ Goal achieved!")
                    exploration_result["success"] = True
                    break
                
                # Check if should pivot strategy
                success_count = sum(1 for h in self.loop_history if h["result"].get("success", False))
                failure_count = sum(1 for h in self.loop_history if not h["result"].get("success", False))
                
                if self.decision.should_pivot_strategy(
                    decision["strategy"],
                    success_count,
                    failure_count,
                    current_state.get("confidence", {}).get("overall", 0.0)
                ):
                    print("  🔀 Pivoting strategy...")
            
            exploration_result["iterations"] = iterations
            exploration_result["final_state"] = current_state
            exploration_result["learned_patterns"] = self._extract_learned_patterns()
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            exploration_result["error"] = str(e)
        
        return exploration_result
    
    def _create_initial_state(self, url: str) -> Dict[str, Any]:
        """Create initial empty state for a URL."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from schemas import create_empty_website_state
        return create_empty_website_state(url)
    
    async def _execute_action(
        self,
        decision: Dict[str, Any],
        state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the decided action.
        
        Args:
            decision: Decision about what to do
            state: Current website state
            goal: Exploration goal
            
        Returns:
            Action execution result
        """
        action = decision["action"]
        strategy = decision["strategy"]
        
        if action == "explore_more":
            return await self._explore_more(state)
        elif action == "use_api":
            return await self._use_api_strategy(state, goal)
        elif action == "use_ui":
            return await self._use_ui_strategy(state, goal)
        elif action == "repeat_successful_pattern":
            return await self._repeat_pattern(state, goal)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    async def _explore_more(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deeper exploration to increase confidence."""
        # Would use browser automation to click around, discover more
        return {
            "success": True,
            "action": "explore_more",
            "discoveries": ["found_more_links", "discovered_forms"],
            "confidence_gain": 0.1
        }
    
    async def _use_api_strategy(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute API-based data extraction."""
        api_endpoints = state.get("capabilities", {}).get("api_endpoints", [])
        
        if not api_endpoints:
            return {
                "success": False,
                "error": "No API endpoints available"
            }
        
        # Would use api-testing MCP to record/replay API calls
        return {
            "success": True,
            "action": "api_extraction",
            "data_extracted": True,
            "quality": 0.85
        }
    
    async def _use_ui_strategy(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute UI-based interaction/extraction."""
        ui_interactions = state.get("capabilities", {}).get("ui_interactions", [])
        
        if not ui_interactions:
            return {
                "success": False,
                "error": "No UI interactions available"
            }
        
        # Would use browser automation to click/scrape
        return {
            "success": True,
            "action": "ui_interaction",
            "data_extracted": True,
            "quality": 0.7
        }
    
    async def _repeat_pattern(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Repeat a previously successful pattern."""
        # Find most recent successful pattern from history
        successful = [h for h in self.loop_history if h["result"].get("success", False)]
        
        if not successful:
            return {
                "success": False,
                "error": "No successful pattern to repeat"
            }
        
        # Repeat the most recent successful action
        last_success = successful[-1]
        return {
            "success": True,
            "action": "repeat_pattern",
            "pattern_used": last_success["decision"]["action"],
            "quality": 0.8
        }
    
    def _learn_from_result(
        self,
        decision: Dict[str, Any],
        result: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Learn patterns from action result.
        
        Args:
            decision: The decision made
            result: The action result
            state: Current state
            
        Returns:
            Learned knowledge
        """
        learned = {
            "pattern": f"{decision['strategy']}_{decision['action']}",
            "success": result.get("success", False),
            "quality": result.get("quality", 0.0),
            "context": {
                "confidence_before": state.get("confidence", {}).get("overall", 0.0),
                "strategy": decision["strategy"]
            }
        }
        
        # Update confidence based on result
        if result.get("success", False):
            confidence_gain = result.get("confidence_gain", 0.1)
            state["confidence"]["overall"] = min(1.0, state["confidence"]["overall"] + confidence_gain)
        
        return learned
    
    def _extract_learned_patterns(self) -> List[Dict[str, Any]]:
        """Extract patterns learned during exploration."""
        patterns = []
        
        for iteration in self.loop_history:
            if iteration["result"].get("success", False):
                patterns.append({
                    "pattern": iteration["learned"]["pattern"],
                    "success_rate": 1.0,  # Would calculate from multiple runs
                    "context": iteration["learned"]["context"]
                })
        
        return patterns
    
    def get_loop_statistics(self) -> Dict[str, Any]:
        """Get statistics about the exploration loop."""
        if not self.loop_history:
            return {"no_data": True}
        
        successes = sum(1 for h in self.loop_history if h["result"].get("success", False))
        total = len(self.loop_history)
        
        strategies_used = {}
        for h in self.loop_history:
            strategy = h["decision"]["strategy"]
            strategies_used[strategy] = strategies_used.get(strategy, 0) + 1
        
        return {
            "total_iterations": total,
            "successes": successes,
            "failures": total - successes,
            "success_rate": successes / total if total > 0 else 0.0,
            "strategies_used": strategies_used,
            "patterns_learned": len(self._extract_learned_patterns())
        }
