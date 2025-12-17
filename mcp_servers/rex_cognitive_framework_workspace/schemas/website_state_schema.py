"""Website State Schema - Mental model for website understanding.

This schema represents Rex's understanding of a website's structure and capabilities.
"""

WEBSITE_STATE_SCHEMA = {
    "type": "object",
    "required": ["url", "timestamp", "structure", "capabilities", "confidence"],
    "properties": {
        "url": {
            "type": "string",
            "description": "Base URL of the website"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "When this state was captured"
        },
        "structure": {
            "type": "object",
            "required": ["dom_summary", "navigation", "content_areas"],
            "properties": {
                "dom_summary": {
                    "type": "object",
                    "properties": {
                        "total_elements": {"type": "integer"},
                        "forms": {"type": "integer"},
                        "buttons": {"type": "integer"},
                        "links": {"type": "integer"},
                        "inputs": {"type": "integer"}
                    }
                },
                "navigation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "url": {"type": "string"},
                            "type": {"type": "string", "enum": ["menu", "link", "button"]}
                        }
                    }
                },
                "content_areas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                }
            }
        },
        "capabilities": {
            "type": "object",
            "required": ["ui_interactions", "api_endpoints", "authentication"],
            "properties": {
                "ui_interactions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "target": {"type": "string"},
                            "success_rate": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                },
                "api_endpoints": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                            "url": {"type": "string"},
                            "discovered_via": {"type": "string", "enum": ["network_capture", "dom_analysis", "documentation"]},
                            "reliability": {"type": "number", "minimum": 0, "maximum": 1},
                            "response_schema": {"type": "object"}
                        }
                    }
                },
                "authentication": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "boolean"},
                        "method": {"type": "string", "enum": ["form", "oauth", "api_key", "session", "unknown"]},
                        "login_url": {"type": "string"},
                        "authenticated": {"type": "boolean"}
                    }
                }
            }
        },
        "confidence": {
            "type": "object",
            "required": ["overall", "breakdown"],
            "properties": {
                "overall": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Overall confidence in understanding (0-1)"
                },
                "breakdown": {
                    "type": "object",
                    "properties": {
                        "structure": {"type": "number", "minimum": 0, "maximum": 1},
                        "capabilities": {"type": "number", "minimum": 0, "maximum": 1},
                        "api_knowledge": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                }
            }
        },
        "metadata": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "technology_stack": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "exploration_count": {"type": "integer", "minimum": 0}
            }
        }
    }
}


def validate_website_state(state: dict) -> tuple[bool, list[str]]:
    """Validate a website state against the schema.
    
    Args:
        state: The website state dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required top-level fields
    required_fields = ["url", "timestamp", "structure", "capabilities", "confidence"]
    for field in required_fields:
        if field not in state:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Validate structure
    if "structure" in state:
        struct = state["structure"]
        required_struct = ["dom_summary", "navigation", "content_areas"]
        for field in required_struct:
            if field not in struct:
                errors.append(f"Missing required structure field: {field}")
    
    # Validate capabilities
    if "capabilities" in state:
        caps = state["capabilities"]
        required_caps = ["ui_interactions", "api_endpoints", "authentication"]
        for field in required_caps:
            if field not in caps:
                errors.append(f"Missing required capabilities field: {field}")
    
    # Validate confidence
    if "confidence" in state:
        conf = state["confidence"]
        if "overall" not in conf:
            errors.append("Missing confidence.overall")
        elif not (0 <= conf["overall"] <= 1):
            errors.append("confidence.overall must be between 0 and 1")
    
    return len(errors) == 0, errors


def create_empty_website_state(url: str) -> dict:
    """Create an empty website state with defaults.
    
    Args:
        url: The website URL
        
    Returns:
        Empty website state dictionary
    """
    from datetime import datetime
    
    return {
        "url": url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "structure": {
            "dom_summary": {
                "total_elements": 0,
                "forms": 0,
                "buttons": 0,
                "links": 0,
                "inputs": 0
            },
            "navigation": [],
            "content_areas": []
        },
        "capabilities": {
            "ui_interactions": [],
            "api_endpoints": [],
            "authentication": {
                "required": False,
                "method": "unknown",
                "login_url": "",
                "authenticated": False
            }
        },
        "confidence": {
            "overall": 0.0,
            "breakdown": {
                "structure": 0.0,
                "capabilities": 0.0,
                "api_knowledge": 0.0
            }
        },
        "metadata": {
            "title": "",
            "description": "",
            "technology_stack": [],
            "exploration_count": 0
        }
    }
