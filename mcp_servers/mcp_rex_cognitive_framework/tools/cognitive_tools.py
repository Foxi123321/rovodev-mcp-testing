"""Cognitive framework tool implementations."""

import sys
import os
from typing import Dict, Any, List

# Import from the workspace framework
WORKSPACE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "OneDrive", "Desktop", "Rexs whishes")
sys.path.insert(0, WORKSPACE_PATH)

try:
    from rex_cognitive_framework.schemas import (
        create_empty_website_state,
        create_exploration_goal as create_goal_schema,
        validate_website_state
    )
    from rex_cognitive_framework.phase1_mental_models import validate_website_state_complete
    from rex_cognitive_framework.phase2_exploration_loop import ExplorationLoop
    from rex_cognitive_framework.phase3_strategy_pivot import PivotEngine
    from rex_cognitive_framework.phase5_validation_persistence import KnowledgeStore
    from rex_cognitive_framework.phase4_integration_test import IntegrationTester
except ImportError as e:
    print(f"Warning: Could not import rex_cognitive_framework: {e}", file=sys.stderr)
    # Provide stub functions if framework not available
    def create_empty_website_state(url): return {"url": url, "error": "Framework not loaded"}
    def create_goal_schema(goal_id, goal_type, description): return {"error": "Framework not loaded"}
    def validate_website_state(state): return (False, ["Framework not loaded"])
    def validate_website_state_complete(state): return (False, ["Framework not loaded"], {})
    class ExplorationLoop: pass
    class PivotEngine: pass
    class KnowledgeStore: pass
    class IntegrationTester: pass


async def explore_website(
    url: str,
    goal_type: str,
    target_description: str,
    max_iterations: int = 10
) -> Dict[str, Any]:
    """Execute full cognitive exploration loop on a website.
    
    Args:
        url: Website URL to explore
        goal_type: Type of goal (discovery, data_extraction, interaction, validation)
        target_description: What to accomplish
        max_iterations: Max exploration iterations
        
    Returns:
        Exploration result with learned state
    """
    try:
        # Create exploration goal
        goal = create_goal_schema(
            goal_id=f"{goal_type}_{url}",
            goal_type=goal_type,
            description=target_description
        )
        
        # Initialize exploration loop
        loop = ExplorationLoop()
        loop.max_iterations = max_iterations
        
        # Run exploration
        result = await loop.explore(url, goal)
        
        return {
            "success": result["success"],
            "iterations": result["iterations"],
            "final_state": result["final_state"],
            "learned_patterns": result["learned_patterns"],
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Exploration failed: {str(e)}"
        }


async def analyze_website_state(url: str, include_vision: bool = False) -> Dict[str, Any]:
    """Analyze a website's current state and structure.
    
    Args:
        url: Website URL
        include_vision: Use vision AI for analysis
        
    Returns:
        Analysis result with confidence scores
    """
    try:
        # NOTE: This MCP server can't directly call other MCP servers
        # The calling agent (RovoDev) needs to orchestrate browser calls
        # We'll return instructions for the agent to follow
        
        return {
            "url": url,
            "valid": True,
            "state": create_empty_website_state(url),
            "requires_browser": True,
            "instructions": {
                "step_1": "Call rex-unstoppable-browser:browse_url with url=" + url,
                "step_2": "Call rex-unstoppable-browser:extract_data with selectors for buttons, links, forms, inputs",
                "step_3": "Call rex-cognitive-framework:analyze_website_state again with extracted data",
                "recommended_selectors": {
                    "buttons": "button, input[type='button'], input[type='submit']",
                    "links": "a[href]",
                    "forms": "form",
                    "inputs": "input, textarea, select",
                    "title": "title",
                    "h1": "h1"
                }
            },
            "confidence_scores": {
                "structure_completeness": 0.0,
                "capabilities_completeness": 0.0,
                "overall_quality": 0.0
            },
            "note": "MCP servers cannot call other MCP servers directly. The agent must orchestrate the browser calls."
        }
        
    except Exception as e:
        return {
            "url": url,
            "valid": False,
            "error": f"Analysis failed: {str(e)}"
        }


def create_exploration_goal(
    goal_type: str,
    target_description: str,
    constraints: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a structured exploration goal.
    
    Args:
        goal_type: Type of goal
        target_description: What to accomplish
        constraints: Optional constraints
        
    Returns:
        Structured exploration goal
    """
    try:
        goal = create_goal_schema(
            goal_id=f"{goal_type}_goal",
            goal_type=goal_type,
            description=target_description
        )
        
        if constraints:
            goal["constraints"] = constraints
        
        return {
            "success": True,
            "goal": goal
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Goal creation failed: {str(e)}"
        }


def validate_website_schema(state: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a website state against the schema.
    
    Args:
        state: Website state to validate
        
    Returns:
        Validation result
    """
    try:
        is_valid, errors = validate_website_state(state)
        
        return {
            "valid": is_valid,
            "errors": errors if errors else [],
            "state": state if is_valid else None
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation failed: {str(e)}"
        }


async def pivot_strategy(
    url: str,
    current_state: Dict[str, Any],
    goal: Dict[str, Any]
) -> Dict[str, Any]:
    """Intelligently switch between UI and API strategies.
    
    Args:
        url: Website URL
        current_state: Current website state
        goal: Exploration goal
        
    Returns:
        Strategy pivot recommendation
    """
    try:
        pivot_engine = PivotEngine()
        
        # Calculate API readiness
        api_readiness = pivot_engine.calculate_api_readiness(current_state)
        
        # Decide strategy
        decision = pivot_engine.decide_strategy(current_state, goal)
        
        return {
            "success": True,
            "api_readiness": api_readiness,
            "recommended_strategy": decision["strategy"],
            "reasoning": decision["reasoning"],
            "confidence": decision["confidence"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Strategy pivot failed: {str(e)}"
        }


async def store_knowledge(
    url: str,
    state: Dict[str, Any],
    patterns: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Store learned patterns and website state.
    
    Args:
        url: Website URL
        state: Website state
        patterns: Learned patterns
        
    Returns:
        Storage result
    """
    try:
        store = KnowledgeStore()
        
        # Store the state
        result = await store.store_website_state(url, state)
        
        # Store patterns if provided
        pattern_count = 0
        if patterns:
            for pattern in patterns:
                await store.store_exploration_pattern(pattern)
                pattern_count += 1
        
        return {
            "success": True,
            "message": result["message"],
            "patterns_stored": pattern_count
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Knowledge storage failed: {str(e)}"
        }


async def retrieve_knowledge(url: str) -> Dict[str, Any]:
    """Retrieve previously learned website state.
    
    Args:
        url: Website URL
        
    Returns:
        Retrieved knowledge
    """
    try:
        store = KnowledgeStore()
        
        # Retrieve state
        state = await store.retrieve_website_state(url)
        
        # Query similar patterns (no direct retrieve_patterns method)
        patterns = await store.query_similar_patterns({"url": url}, limit=10)
        
        if state:
            return {
                "success": True,
                "url": url,
                "state": state,
                "patterns": patterns if patterns else []
            }
        else:
            return {
                "success": False,
                "message": f"No knowledge found for {url}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Knowledge retrieval failed: {str(e)}"
        }


async def run_integration_test(scenario: str = "all") -> Dict[str, Any]:
    """Run full integration test across all phases.
    
    Args:
        scenario: Test scenario (ecommerce, news, api, or all)
        
    Returns:
        Test results
    """
    try:
        tester = IntegrationTester()
        
        if scenario == "all":
            results = await tester.run_full_test_suite()
        else:
            # Run specific scenario
            scenario_map = {
                "ecommerce": "E-commerce Product Extraction",
                "news": "News Site Discovery",
                "api": "API-First Data Retrieval"
            }
            
            if scenario not in scenario_map:
                return {
                    "success": False,
                    "error": f"Unknown scenario: {scenario}"
                }
            
            # Run single test
            result = await tester.run_integration_test(
                scenario_map[scenario],
                f"https://example-{scenario}.com",
                "data_extraction" if scenario == "ecommerce" else "discovery"
            )
            
            results = {
                "success": result["success"],
                "results": [result],
                "success_rate": 1.0 if result["success"] else 0.0
            }
        
        return {
            "success": results["success_rate"] > 0.5,
            "results": results["results"],
            "success_rate": results["success_rate"],
            "total_tests": len(results["results"])
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Integration test failed: {str(e)}"
        }
