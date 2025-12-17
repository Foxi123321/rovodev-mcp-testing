"""Exploration Goal Schema - Defines what Rex wants to achieve on a website."""

EXPLORATION_GOAL_SCHEMA = {
    "type": "object",
    "required": ["goal_id", "goal_type", "target", "success_criteria", "constraints"],
    "properties": {
        "goal_id": {
            "type": "string",
            "description": "Unique identifier for this goal"
        },
        "goal_type": {
            "type": "string",
            "enum": ["data_extraction", "interaction", "discovery", "validation"],
            "description": "Type of exploration goal"
        },
        "target": {
            "type": "object",
            "required": ["description", "specifics"],
            "properties": {
                "description": {
                    "type": "string",
                    "description": "High-level description of what to find/do"
                },
                "specifics": {
                    "type": "object",
                    "properties": {
                        "selectors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "CSS selectors to target"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keywords to search for"
                        },
                        "patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Regex patterns to match"
                        }
                    }
                }
            }
        },
        "success_criteria": {
            "type": "object",
            "required": ["must_have", "nice_to_have"],
            "properties": {
                "must_have": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Requirements that MUST be met"
                },
                "nice_to_have": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional success indicators"
                },
                "quality_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Minimum quality score (0-1) to consider success"
                }
            }
        },
        "constraints": {
            "type": "object",
            "properties": {
                "max_time_seconds": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Maximum time allowed for this goal"
                },
                "max_attempts": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Maximum exploration attempts"
                },
                "require_authentication": {
                    "type": "boolean",
                    "description": "Whether authentication is required"
                },
                "preferred_strategy": {
                    "type": "string",
                    "enum": ["ui_first", "api_first", "adaptive"],
                    "description": "Preferred exploration strategy"
                }
            }
        },
        "context": {
            "type": "object",
            "properties": {
                "past_attempts": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of past attempts at this goal"
                },
                "past_success_rate": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Success rate from past attempts"
                },
                "learned_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Patterns learned from past exploration"
                }
            }
        }
    }
}


def validate_exploration_goal(goal: dict) -> tuple[bool, list[str]]:
    """Validate an exploration goal against the schema.
    
    Args:
        goal: The exploration goal dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required top-level fields
    required_fields = ["goal_id", "goal_type", "target", "success_criteria", "constraints"]
    for field in required_fields:
        if field not in goal:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Validate goal_type
    valid_types = ["data_extraction", "interaction", "discovery", "validation"]
    if goal.get("goal_type") not in valid_types:
        errors.append(f"Invalid goal_type. Must be one of: {valid_types}")
    
    # Validate target
    if "target" in goal:
        target = goal["target"]
        if "description" not in target:
            errors.append("Missing target.description")
        if "specifics" not in target:
            errors.append("Missing target.specifics")
    
    # Validate success_criteria
    if "success_criteria" in goal:
        criteria = goal["success_criteria"]
        if "must_have" not in criteria:
            errors.append("Missing success_criteria.must_have")
        if "nice_to_have" not in criteria:
            errors.append("Missing success_criteria.nice_to_have")
        
        if "quality_threshold" in criteria:
            threshold = criteria["quality_threshold"]
            if not (0 <= threshold <= 1):
                errors.append("success_criteria.quality_threshold must be between 0 and 1")
    
    # Validate constraints
    if "constraints" in goal:
        constraints = goal["constraints"]
        
        if "max_time_seconds" in constraints and constraints["max_time_seconds"] < 1:
            errors.append("constraints.max_time_seconds must be >= 1")
        
        if "max_attempts" in constraints and constraints["max_attempts"] < 1:
            errors.append("constraints.max_attempts must be >= 1")
        
        if "preferred_strategy" in constraints:
            valid_strategies = ["ui_first", "api_first", "adaptive"]
            if constraints["preferred_strategy"] not in valid_strategies:
                errors.append(f"Invalid preferred_strategy. Must be one of: {valid_strategies}")
    
    return len(errors) == 0, errors


def create_exploration_goal(goal_id: str, goal_type: str, description: str) -> dict:
    """Create a basic exploration goal with defaults.
    
    Args:
        goal_id: Unique identifier for the goal
        goal_type: Type of goal (data_extraction, interaction, discovery, validation)
        description: Description of what to achieve
        
    Returns:
        Exploration goal dictionary
    """
    return {
        "goal_id": goal_id,
        "goal_type": goal_type,
        "target": {
            "description": description,
            "specifics": {
                "selectors": [],
                "keywords": [],
                "patterns": []
            }
        },
        "success_criteria": {
            "must_have": [],
            "nice_to_have": [],
            "quality_threshold": 0.7
        },
        "constraints": {
            "max_time_seconds": 60,
            "max_attempts": 3,
            "require_authentication": False,
            "preferred_strategy": "adaptive"
        },
        "context": {
            "past_attempts": 0,
            "past_success_rate": 0.0,
            "learned_patterns": []
        }
    }
