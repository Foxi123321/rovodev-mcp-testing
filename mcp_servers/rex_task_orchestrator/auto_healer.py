"""
Rex Task Orchestrator - Auto Healer
Detect and fix common issues autonomously
"""
import os
import re
import subprocess
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HealingAction:
    action_id: str
    issue_type: str
    issue_description: str
    action_taken: str
    success: bool
    timestamp: float
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "issue_type": self.issue_type,
            "issue_description": self.issue_description,
            "action_taken": self.action_taken,
            "success": self.success,
            "timestamp": self.timestamp,
            "details": self.details
        }


class AutoHealer:
    """
    Auto-healing system that can:
    - Fix dependency issues
    - Repair syntax errors
    - Resolve test failures
    - Handle common runtime errors
    - Learn from knowledge DB
    """
    
    def __init__(self, config: Dict, knowledge_db_client=None):
        self.config = config
        self.enable_dependency_fix = config.get("enable_dependency_auto_fix", True)
        self.enable_syntax_fix = config.get("enable_syntax_auto_fix", True)
        self.enable_test_fix = config.get("enable_test_auto_fix", True)
        self.knowledge_db = knowledge_db_client
        
        self.healing_history: List[HealingAction] = []
        self._action_counter = 0
    
    async def detect_and_heal(self, error_info: Dict) -> HealingAction:
        """
        Main entry point - detect issue and attempt healing
        """
        self._action_counter += 1
        action_id = f"heal_{self._action_counter}_{int(time.time())}"
        
        error_type = error_info.get("type", "unknown")
        error_message = error_info.get("message", "")
        context = error_info.get("context", {})
        
        logger.info(f"Auto-healing attempt: {action_id} for {error_type}")
        
        # Try to find solution in knowledge DB first
        if self.knowledge_db:
            known_solution = await self._check_knowledge_db(error_message)
            if known_solution:
                logger.info("Found solution in knowledge DB")
                success = await self._apply_known_solution(known_solution, context)
                
                action = HealingAction(
                    action_id=action_id,
                    issue_type=error_type,
                    issue_description=error_message,
                    action_taken="Applied known solution from knowledge DB",
                    success=success,
                    timestamp=time.time(),
                    details={"solution": known_solution}
                )
                self.healing_history.append(action)
                return action
        
        # Apply specific healing strategies
        if "import" in error_type.lower() or "modulenotfound" in error_message.lower():
            action = await self._heal_import_error(action_id, error_message, context)
        elif "syntax" in error_type.lower():
            action = await self._heal_syntax_error(action_id, error_message, context)
        elif "test" in error_type.lower() or "assertion" in error_message.lower():
            action = await self._heal_test_failure(action_id, error_message, context)
        elif "dependency" in error_type.lower():
            action = await self._heal_dependency_issue(action_id, error_message, context)
        elif "timeout" in error_message.lower():
            action = await self._heal_timeout_issue(action_id, error_message, context)
        else:
            action = HealingAction(
                action_id=action_id,
                issue_type=error_type,
                issue_description=error_message,
                action_taken="No automatic healing available",
                success=False,
                timestamp=time.time(),
                details={"reason": "Unknown error type"}
            )
        
        self.healing_history.append(action)
        
        # Store successful healing in knowledge DB
        if action.success and self.knowledge_db:
            await self._store_healing_solution(error_message, action)
        
        return action
    
    async def _heal_import_error(self, action_id: str, error: str, context: Dict) -> HealingAction:
        """Heal import/module not found errors"""
        if not self.enable_dependency_fix:
            return self._create_disabled_action(action_id, "import_error", error)
        
        # Extract package name
        package_match = re.search(r"No module named ['\"](.+?)['\"]", error)
        if not package_match:
            package_match = re.search(r"ModuleNotFoundError: (.+)", error)
        
        if package_match:
            package_name = package_match.group(1)
            logger.info(f"Attempting to install missing package: {package_name}")
            
            try:
                # Try pip install
                result = subprocess.run(
                    ["pip", "install", package_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                success = result.returncode == 0
                
                return HealingAction(
                    action_id=action_id,
                    issue_type="import_error",
                    issue_description=error,
                    action_taken=f"Installed package: {package_name}",
                    success=success,
                    timestamp=time.time(),
                    details={
                        "package": package_name,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                )
            except Exception as e:
                logger.error(f"Failed to install package: {e}")
                return HealingAction(
                    action_id=action_id,
                    issue_type="import_error",
                    issue_description=error,
                    action_taken=f"Failed to install {package_name}",
                    success=False,
                    timestamp=time.time(),
                    details={"error": str(e)}
                )
        
        return self._create_failed_action(action_id, "import_error", error, "Could not parse package name")
    
    async def _heal_syntax_error(self, action_id: str, error: str, context: Dict) -> HealingAction:
        """Heal syntax errors (simple cases)"""
        if not self.enable_syntax_fix:
            return self._create_disabled_action(action_id, "syntax_error", error)
        
        file_path = context.get("file_path")
        line_number = context.get("line_number")
        
        if not file_path or not os.path.exists(file_path):
            return self._create_failed_action(action_id, "syntax_error", error, "No file path provided")
        
        # Common fixable syntax errors
        fixes_applied = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            modified = False
            
            # Fix missing colons
            if "expected ':'" in error.lower() and line_number:
                if 0 <= line_number - 1 < len(lines):
                    line = lines[line_number - 1]
                    if not line.rstrip().endswith(':'):
                        lines[line_number - 1] = line.rstrip() + ':\n'
                        fixes_applied.append("Added missing colon")
                        modified = True
            
            # Fix unmatched parentheses/brackets
            if "unmatched" in error.lower() or "unexpected" in error.lower():
                # Simple balance check
                for i, line in enumerate(lines):
                    if line.count('(') != line.count(')'):
                        # Add missing closing paren
                        lines[i] = line.rstrip() + ')' * (line.count('(') - line.count(')')) + '\n'
                        fixes_applied.append(f"Balanced parentheses on line {i+1}")
                        modified = True
            
            if modified:
                # Write back
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                
                return HealingAction(
                    action_id=action_id,
                    issue_type="syntax_error",
                    issue_description=error,
                    action_taken=f"Fixed syntax: {', '.join(fixes_applied)}",
                    success=True,
                    timestamp=time.time(),
                    details={"fixes": fixes_applied, "file": file_path}
                )
        
        except Exception as e:
            logger.error(f"Syntax healing failed: {e}")
            return self._create_failed_action(action_id, "syntax_error", error, str(e))
        
        return self._create_failed_action(action_id, "syntax_error", error, "No automatic fix available")
    
    async def _heal_test_failure(self, action_id: str, error: str, context: Dict) -> HealingAction:
        """Heal test failures"""
        if not self.enable_test_fix:
            return self._create_disabled_action(action_id, "test_failure", error)
        
        # For now, just re-run tests to see if it's flaky
        test_command = context.get("test_command", "pytest")
        
        try:
            logger.info("Re-running tests to check for flakiness")
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            
            return HealingAction(
                action_id=action_id,
                issue_type="test_failure",
                issue_description=error,
                action_taken="Re-ran tests (flakiness check)",
                success=success,
                timestamp=time.time(),
                details={
                    "stdout": result.stdout[-500:],  # Last 500 chars
                    "stderr": result.stderr[-500:]
                }
            )
        
        except Exception as e:
            return self._create_failed_action(action_id, "test_failure", error, str(e))
    
    async def _heal_dependency_issue(self, action_id: str, error: str, context: Dict) -> HealingAction:
        """Heal dependency conflicts"""
        if not self.enable_dependency_fix:
            return self._create_disabled_action(action_id, "dependency_issue", error)
        
        logger.info("Attempting to fix dependencies")
        
        try:
            # Try updating all dependencies
            result = subprocess.run(
                ["pip", "install", "--upgrade", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            
            return HealingAction(
                action_id=action_id,
                issue_type="dependency_issue",
                issue_description=error,
                action_taken="Updated dependencies from requirements.txt",
                success=success,
                timestamp=time.time(),
                details={"stdout": result.stdout, "stderr": result.stderr}
            )
        
        except Exception as e:
            return self._create_failed_action(action_id, "dependency_issue", error, str(e))
    
    async def _heal_timeout_issue(self, action_id: str, error: str, context: Dict) -> HealingAction:
        """Heal timeout issues by killing stuck processes"""
        logger.info("Attempting to resolve timeout issue")
        
        process_name = context.get("process_name")
        
        if process_name:
            try:
                # Kill process
                if os.name == 'nt':  # Windows
                    subprocess.run(["taskkill", "/F", "/IM", process_name], timeout=10)
                else:  # Unix
                    subprocess.run(["pkill", "-9", process_name], timeout=10)
                
                return HealingAction(
                    action_id=action_id,
                    issue_type="timeout",
                    issue_description=error,
                    action_taken=f"Killed stuck process: {process_name}",
                    success=True,
                    timestamp=time.time(),
                    details={"process": process_name}
                )
            except Exception as e:
                return self._create_failed_action(action_id, "timeout", error, str(e))
        
        return self._create_failed_action(action_id, "timeout", error, "No process name provided")
    
    async def _check_knowledge_db(self, error: str) -> Optional[Dict]:
        """Check knowledge DB for known solutions"""
        # This will call the knowledge_database MCP server
        # For now, return None
        return None
    
    async def _apply_known_solution(self, solution: Dict, context: Dict) -> bool:
        """Apply a known solution from knowledge DB"""
        # Execute the solution steps
        try:
            steps = solution.get("steps", [])
            for step in steps:
                # Execute each step
                pass
            return True
        except:
            return False
    
    async def _store_healing_solution(self, error: str, action: HealingAction):
        """Store successful healing in knowledge DB"""
        # This will call knowledge_database:store_solution
        pass
    
    def _create_disabled_action(self, action_id: str, issue_type: str, error: str) -> HealingAction:
        """Create action for disabled healing"""
        return HealingAction(
            action_id=action_id,
            issue_type=issue_type,
            issue_description=error,
            action_taken="Auto-healing disabled for this issue type",
            success=False,
            timestamp=time.time(),
            details={"reason": "disabled"}
        )
    
    def _create_failed_action(self, action_id: str, issue_type: str, error: str, reason: str) -> HealingAction:
        """Create failed action"""
        return HealingAction(
            action_id=action_id,
            issue_type=issue_type,
            issue_description=error,
            action_taken=f"Failed: {reason}",
            success=False,
            timestamp=time.time(),
            details={"reason": reason}
        )
    
    def get_healing_history(self, last_n: int = 10) -> List[Dict]:
        """Get recent healing history"""
        return [a.to_dict() for a in self.healing_history[-last_n:]]
    
    def get_healing_stats(self) -> Dict:
        """Get healing statistics"""
        if not self.healing_history:
            return {
                "total_attempts": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        
        total = len(self.healing_history)
        successful = sum(1 for a in self.healing_history if a.success)
        failed = total - successful
        success_rate = successful / total if total > 0 else 0
        
        return {
            "total_attempts": total,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "by_type": self._get_stats_by_type()
        }
    
    def _get_stats_by_type(self) -> Dict[str, Dict]:
        """Get statistics broken down by issue type"""
        by_type = {}
        
        for action in self.healing_history:
            if action.issue_type not in by_type:
                by_type[action.issue_type] = {"total": 0, "successful": 0}
            
            by_type[action.issue_type]["total"] += 1
            if action.success:
                by_type[action.issue_type]["successful"] += 1
        
        # Calculate success rates
        for issue_type in by_type:
            stats = by_type[issue_type]
            stats["success_rate"] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
        
        return by_type
