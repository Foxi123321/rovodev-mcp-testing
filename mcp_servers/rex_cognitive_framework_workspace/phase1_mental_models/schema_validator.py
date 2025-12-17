"""Schema validation utilities for Phase 1."""

import json
from typing import Dict, Any, Tuple, List


class SchemaValidator:
    """Validates data against JSON schemas."""
    
    def __init__(self):
        """Initialize the schema validator."""
        pass
    
    def validate(self, data: Dict[Any, Any], schema: Dict[Any, Any]) -> Tuple[bool, List[str]]:
        """Validate data against a schema.
        
        Args:
            data: The data to validate
            schema: The JSON schema to validate against
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check type
        if "type" in schema:
            expected_type = schema["type"]
            actual_type = self._get_type(data)
            
            if actual_type != expected_type:
                errors.append(f"Type mismatch: expected {expected_type}, got {actual_type}")
                return False, errors
        
        # Check required fields (for objects)
        if schema.get("type") == "object" and "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        
        # Validate properties (for objects)
        if schema.get("type") == "object" and "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                if prop in data:
                    is_valid, prop_errors = self.validate(data[prop], prop_schema)
                    if not is_valid:
                        errors.extend([f"{prop}.{err}" for err in prop_errors])
        
        # Validate items (for arrays)
        if schema.get("type") == "array" and "items" in schema and isinstance(data, list):
            for i, item in enumerate(data):
                is_valid, item_errors = self.validate(item, schema["items"])
                if not is_valid:
                    errors.extend([f"[{i}].{err}" for err in item_errors])
        
        # Check enum values
        if "enum" in schema:
            if data not in schema["enum"]:
                errors.append(f"Value '{data}' not in allowed enum: {schema['enum']}")
        
        # Check number constraints
        if schema.get("type") in ["number", "integer"]:
            if "minimum" in schema and data < schema["minimum"]:
                errors.append(f"Value {data} is less than minimum {schema['minimum']}")
            if "maximum" in schema and data > schema["maximum"]:
                errors.append(f"Value {data} is greater than maximum {schema['maximum']}")
        
        return len(errors) == 0, errors
    
    def _get_type(self, data: Any) -> str:
        """Get the JSON schema type of data.
        
        Args:
            data: The data to check
            
        Returns:
            JSON schema type string
        """
        if isinstance(data, bool):
            return "boolean"
        elif isinstance(data, int):
            return "integer"
        elif isinstance(data, float):
            return "number"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, dict):
            return "object"
        elif data is None:
            return "null"
        else:
            return "unknown"
    
    def validate_json_file(self, file_path: str, schema: Dict[Any, Any]) -> Tuple[bool, List[str]]:
        """Validate a JSON file against a schema.
        
        Args:
            file_path: Path to JSON file
            schema: The JSON schema to validate against
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.validate(data, schema)
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {str(e)}"]
        except Exception as e:
            return False, [f"Error validating file: {str(e)}"]


def validate_website_state_complete(state: Dict[Any, Any]) -> Tuple[bool, List[str], Dict[str, float]]:
    """Complete validation of website state with confidence scoring.
    
    Args:
        state: The website state to validate
        
    Returns:
        Tuple of (is_valid, errors, confidence_scores)
    """
    from ..schemas import validate_website_state
    
    is_valid, errors = validate_website_state(state)
    
    # Calculate confidence scores
    confidence_scores = {
        "structure_completeness": 0.0,
        "capabilities_completeness": 0.0,
        "overall_quality": 0.0
    }
    
    if is_valid and "structure" in state:
        # Score structure completeness
        struct = state["structure"]
        structure_score = 0.0
        
        if "dom_summary" in struct and struct["dom_summary"].get("total_elements", 0) > 0:
            structure_score += 0.3
        if "navigation" in struct and len(struct["navigation"]) > 0:
            structure_score += 0.3
        if "content_areas" in struct and len(struct["content_areas"]) > 0:
            structure_score += 0.4
        
        confidence_scores["structure_completeness"] = structure_score
    
    if is_valid and "capabilities" in state:
        # Score capabilities completeness
        caps = state["capabilities"]
        caps_score = 0.0
        
        if "ui_interactions" in caps and len(caps["ui_interactions"]) > 0:
            caps_score += 0.3
        if "api_endpoints" in caps and len(caps["api_endpoints"]) > 0:
            caps_score += 0.4
        if "authentication" in caps and caps["authentication"].get("method") != "unknown":
            caps_score += 0.3
        
        confidence_scores["capabilities_completeness"] = caps_score
    
    # Overall quality score
    if is_valid:
        confidence_scores["overall_quality"] = (
            confidence_scores["structure_completeness"] * 0.4 +
            confidence_scores["capabilities_completeness"] * 0.6
        )
    
    return is_valid, errors, confidence_scores
