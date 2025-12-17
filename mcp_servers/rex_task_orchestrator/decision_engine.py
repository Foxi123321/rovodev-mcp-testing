"""
Rex Task Orchestrator - Decision Engine
Autonomous decision-making based on rules, patterns, and context
"""
import time
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionType(Enum):
    RULE_BASED = "rule_based"
    PATTERN_BASED = "pattern_based"
    THRESHOLD_BASED = "threshold_based"
    ML_BASED = "ml_based"


@dataclass
class Decision:
    decision_id: str
    decision_type: DecisionType
    context: Dict[str, Any]
    result: Any
    confidence: float
    reasoning: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "context": self.context,
            "result": self.result,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }


@dataclass
class Rule:
    rule_id: str
    name: str
    condition: Callable[[Dict], bool]
    action: Callable[[Dict], Any]
    priority: int = 0
    enabled: bool = True
    description: str = ""


class DecisionEngine:
    """
    Autonomous decision engine that can:
    - Apply rule-based logic
    - Detect patterns from history
    - Make threshold-based decisions
    - Learn from past decisions
    """
    
    def __init__(self, knowledge_db_client=None):
        self.rules: Dict[str, Rule] = {}
        self.decision_history: List[Decision] = []
        self.patterns: Dict[str, List[Dict]] = {}
        self.knowledge_db = knowledge_db_client
        self._decision_counter = 0
    
    def add_rule(
        self,
        name: str,
        condition: Callable[[Dict], bool],
        action: Callable[[Dict], Any],
        priority: int = 0,
        description: str = ""
    ) -> str:
        """Add a decision rule"""
        rule_id = f"rule_{len(self.rules)}_{int(time.time())}"
        
        rule = Rule(
            rule_id=rule_id,
            name=name,
            condition=condition,
            action=action,
            priority=priority,
            description=description
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Rule added: {name} (priority: {priority})")
        
        return rule_id
    
    def make_decision(self, context: Dict[str, Any], decision_type: DecisionType = DecisionType.RULE_BASED) -> Decision:
        """Make a decision based on context"""
        self._decision_counter += 1
        decision_id = f"decision_{self._decision_counter}_{int(time.time())}"
        
        logger.info(f"Making decision: {decision_id} (type: {decision_type.value})")
        
        if decision_type == DecisionType.RULE_BASED:
            result, confidence, reasoning = self._apply_rules(context)
        elif decision_type == DecisionType.PATTERN_BASED:
            result, confidence, reasoning = self._apply_patterns(context)
        elif decision_type == DecisionType.THRESHOLD_BASED:
            result, confidence, reasoning = self._apply_thresholds(context)
        else:
            result, confidence, reasoning = None, 0.0, "Unknown decision type"
        
        decision = Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            context=context,
            result=result,
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.decision_history.append(decision)
        
        logger.info(f"Decision made: {result} (confidence: {confidence:.2f})")
        
        return decision
    
    def _apply_rules(self, context: Dict) -> tuple[Any, float, str]:
        """Apply rule-based decision making"""
        # Sort rules by priority
        sorted_rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            try:
                if rule.condition(context):
                    result = rule.action(context)
                    reasoning = f"Rule '{rule.name}' matched and executed"
                    return result, 1.0, reasoning
            except Exception as e:
                logger.error(f"Rule execution error: {rule.name} - {e}")
        
        return None, 0.0, "No matching rules found"
    
    def _apply_patterns(self, context: Dict) -> tuple[Any, float, str]:
        """Apply pattern-based decision making"""
        # Look for similar past decisions
        similar_decisions = self._find_similar_decisions(context)
        
        if not similar_decisions:
            return None, 0.0, "No similar patterns found"
        
        # Aggregate results from similar decisions
        results = [d.result for d in similar_decisions]
        
        # Find most common result
        if results:
            most_common = max(set(results), key=results.count)
            confidence = results.count(most_common) / len(results)
            reasoning = f"Pattern detected from {len(similar_decisions)} similar past decisions"
            return most_common, confidence, reasoning
        
        return None, 0.0, "Could not determine pattern"
    
    def _apply_thresholds(self, context: Dict) -> tuple[Any, float, str]:
        """Apply threshold-based decision making"""
        # Common threshold checks
        thresholds = {
            "cpu_high": ("cpu_percent", 85, "CPU usage is high"),
            "memory_high": ("memory_percent", 90, "Memory usage is high"),
            "disk_high": ("disk_percent", 95, "Disk usage is critical"),
            "error_rate_high": ("error_rate", 0.05, "Error rate is too high"),
            "response_time_slow": ("response_time_ms", 1000, "Response time is slow")
        }
        
        triggered = []
        for threshold_name, (key, value, message) in thresholds.items():
            if key in context and context[key] > value:
                triggered.append(message)
        
        if triggered:
            result = {"action": "alert", "reasons": triggered}
            confidence = 0.9
            reasoning = f"Thresholds exceeded: {', '.join(triggered)}"
            return result, confidence, reasoning
        
        return {"action": "no_action"}, 1.0, "All metrics within normal range"
    
    def _find_similar_decisions(self, context: Dict, limit: int = 10) -> List[Decision]:
        """Find similar past decisions based on context"""
        similar = []
        
        for decision in self.decision_history[-100:]:  # Look at last 100
            similarity = self._calculate_similarity(context, decision.context)
            if similarity > 0.7:  # 70% similarity threshold
                similar.append(decision)
        
        return similar[-limit:]
    
    def _calculate_similarity(self, context1: Dict, context2: Dict) -> float:
        """Calculate similarity between two contexts"""
        # Simple key matching
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0
        
        matching_values = sum(
            1 for key in common_keys
            if context1.get(key) == context2.get(key)
        )
        
        return matching_values / len(common_keys)
    
    def should_auto_fix(self, error_type: str, context: Dict) -> Dict:
        """Decide if error should be auto-fixed"""
        # Common auto-fixable errors
        auto_fixable = {
            "import_error": lambda ctx: ctx.get("missing_package") is not None,
            "syntax_error": lambda ctx: ctx.get("simple_syntax", False),
            "test_failure": lambda ctx: ctx.get("deterministic", True),
            "dependency_issue": lambda ctx: True,
            "formatting_error": lambda ctx: True
        }
        
        if error_type in auto_fixable:
            try:
                should_fix = auto_fixable[error_type](context)
                if should_fix:
                    return {
                        "auto_fix": True,
                        "confidence": 0.85,
                        "reasoning": f"{error_type} is typically auto-fixable"
                    }
            except:
                pass
        
        return {
            "auto_fix": False,
            "confidence": 0.0,
            "reasoning": f"{error_type} requires manual intervention"
        }
    
    def should_retry_task(self, task_result: Dict, retry_count: int) -> Dict:
        """Decide if failed task should be retried"""
        max_retries = 3
        
        # Don't retry if max attempts reached
        if retry_count >= max_retries:
            return {
                "retry": False,
                "reasoning": "Max retries reached"
            }
        
        # Analyze failure type
        error_type = task_result.get("error_type", "unknown")
        
        # Transient errors - always retry
        transient_errors = ["timeout", "connection_error", "rate_limit", "temporary"]
        if any(err in error_type.lower() for err in transient_errors):
            return {
                "retry": True,
                "wait_seconds": 2 ** retry_count,  # Exponential backoff
                "reasoning": "Transient error detected"
            }
        
        # Permanent errors - don't retry
        permanent_errors = ["not_found", "unauthorized", "invalid_input", "syntax"]
        if any(err in error_type.lower() for err in permanent_errors):
            return {
                "retry": False,
                "reasoning": "Permanent error - retry won't help"
            }
        
        # Unknown - retry once
        if retry_count == 0:
            return {
                "retry": True,
                "wait_seconds": 1,
                "reasoning": "Unknown error - attempting one retry"
            }
        
        return {
            "retry": False,
            "reasoning": "Unknown error persists"
        }
    
    def get_decision_history(self, last_n: int = 10) -> List[Dict]:
        """Get recent decision history"""
        return [d.to_dict() for d in self.decision_history[-last_n:]]
    
    def get_rule_list(self) -> List[Dict]:
        """Get all rules"""
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "priority": rule.priority,
                "enabled": rule.enabled,
                "description": rule.description
            }
            for rule in self.rules.values()
        ]
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Rule enabled: {rule_id}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Rule disabled: {rule_id}")
            return True
        return False
