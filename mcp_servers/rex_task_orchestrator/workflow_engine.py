"""
Rex Task Orchestrator - Workflow Engine
Build and execute multi-step workflows with conditional logic
"""
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    step_id: str
    name: str
    action: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    condition: Optional[Callable] = None  # Function that returns bool
    on_success: Optional[str] = None  # Next step ID on success
    on_failure: Optional[str] = None  # Next step ID on failure
    retry_on_failure: bool = False
    max_retries: int = 3
    timeout_seconds: Optional[int] = None
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class Workflow:
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step_index: int = 0
    context: Dict[str, Any] = field(default_factory=dict)  # Shared data between steps
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None


class WorkflowEngine:
    """
    Execute complex workflows with:
    - Sequential steps
    - Conditional branching
    - Error handling
    - Retry logic
    - Context sharing between steps
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self._workflow_counter = 0
    
    def create_workflow(
        self,
        name: str,
        description: str = "",
        steps: Optional[List[Dict]] = None
    ) -> str:
        """Create a new workflow"""
        self._workflow_counter += 1
        workflow_id = f"workflow_{self._workflow_counter}_{int(time.time())}"
        
        workflow_steps = []
        if steps:
            for i, step_config in enumerate(steps):
                step = WorkflowStep(
                    step_id=f"{workflow_id}_step_{i}",
                    name=step_config.get("name", f"Step {i+1}"),
                    action=step_config["action"],
                    args=step_config.get("args", ()),
                    kwargs=step_config.get("kwargs", {}),
                    condition=step_config.get("condition"),
                    on_success=step_config.get("on_success"),
                    on_failure=step_config.get("on_failure"),
                    retry_on_failure=step_config.get("retry_on_failure", False),
                    max_retries=step_config.get("max_retries", 3),
                    timeout_seconds=step_config.get("timeout_seconds")
                )
                workflow_steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow created: {workflow_id} - {name} ({len(workflow_steps)} steps)")
        
        return workflow_id
    
    def add_step(
        self,
        workflow_id: str,
        name: str,
        action: Callable,
        args: tuple = (),
        kwargs: dict = None,
        condition: Optional[Callable] = None,
        on_success: Optional[str] = None,
        on_failure: Optional[str] = None,
        retry_on_failure: bool = False,
        max_retries: int = 3
    ) -> str:
        """Add a step to an existing workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        step_index = len(workflow.steps)
        step_id = f"{workflow_id}_step_{step_index}"
        
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            action=action,
            args=args,
            kwargs=kwargs or {},
            condition=condition,
            on_success=on_success,
            on_failure=on_failure,
            retry_on_failure=retry_on_failure,
            max_retries=max_retries
        )
        
        workflow.steps.append(step)
        logger.info(f"Step added to {workflow_id}: {name}")
        
        return step_id
    
    async def execute_workflow(self, workflow_id: str) -> Dict:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = time.time()
        workflow.current_step_index = 0
        
        logger.info(f"Starting workflow: {workflow_id} - {workflow.name}")
        
        try:
            while workflow.current_step_index < len(workflow.steps):
                step = workflow.steps[workflow.current_step_index]
                
                # Check condition if exists
                if step.condition:
                    try:
                        should_execute = step.condition(workflow.context)
                        if not should_execute:
                            logger.info(f"Step skipped (condition failed): {step.name}")
                            step.status = StepStatus.SKIPPED
                            workflow.current_step_index += 1
                            continue
                    except Exception as e:
                        logger.error(f"Condition evaluation failed: {e}")
                        step.status = StepStatus.FAILED
                        step.error = str(e)
                        break
                
                # Execute step
                step_result = await self._execute_step(workflow, step)
                
                if step.status == StepStatus.FAILED:
                    if step.on_failure:
                        # Jump to failure handler step
                        failure_step_id = step.on_failure
                        workflow.current_step_index = self._find_step_index(workflow, failure_step_id)
                    else:
                        # Workflow failed
                        workflow.status = WorkflowStatus.FAILED
                        break
                elif step.status == StepStatus.COMPLETED:
                    if step.on_success:
                        # Jump to success handler step
                        success_step_id = step.on_success
                        workflow.current_step_index = self._find_step_index(workflow, success_step_id)
                    else:
                        # Move to next step
                        workflow.current_step_index += 1
            
            # All steps completed
            if workflow.current_step_index >= len(workflow.steps):
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = time.time()
                logger.info(f"Workflow completed: {workflow_id}")
        
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = time.time()
        
        return self.get_workflow_status(workflow_id)
    
    async def _execute_step(self, workflow: Workflow, step: WorkflowStep) -> Any:
        """Execute a single workflow step"""
        step.status = StepStatus.RUNNING
        step.started_at = time.time()
        
        logger.info(f"Executing step: {step.name}")
        
        retries = 0
        while retries <= (step.max_retries if step.retry_on_failure else 0):
            try:
                # Inject workflow context into kwargs
                kwargs = {**step.kwargs, "workflow_context": workflow.context}
                
                # Execute action
                import asyncio
                if asyncio.iscoroutinefunction(step.action):
                    result = await step.action(*step.args, **kwargs)
                else:
                    result = step.action(*step.args, **kwargs)
                
                step.result = result
                step.status = StepStatus.COMPLETED
                step.completed_at = time.time()
                
                # Store result in workflow context
                workflow.context[step.step_id] = result
                
                duration = step.completed_at - step.started_at
                logger.info(f"Step completed: {step.name} in {duration:.2f}s")
                
                return result
            
            except Exception as e:
                logger.error(f"Step failed: {step.name} - {e}")
                
                if step.retry_on_failure and retries < step.max_retries:
                    retries += 1
                    logger.info(f"Retrying step: {step.name} (attempt {retries}/{step.max_retries})")
                    time.sleep(1)  # Wait before retry
                else:
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    step.completed_at = time.time()
                    return None
        
        return None
    
    def _find_step_index(self, workflow: Workflow, step_id: str) -> int:
        """Find the index of a step by ID"""
        for i, step in enumerate(workflow.steps):
            if step.step_id == step_id:
                return i
        return workflow.current_step_index + 1  # Continue to next if not found
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get workflow status"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        steps_status = []
        for step in workflow.steps:
            steps_status.append({
                "step_id": step.step_id,
                "name": step.name,
                "status": step.status.value,
                "result": step.result,
                "error": step.error,
                "started_at": step.started_at,
                "completed_at": step.completed_at
            })
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value,
            "current_step": workflow.current_step_index,
            "total_steps": len(workflow.steps),
            "steps": steps_status,
            "context": workflow.context,
            "created_at": workflow.created_at,
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at
        }
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            logger.info(f"Workflow paused: {workflow_id}")
            return True
        return False
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            logger.info(f"Workflow resumed: {workflow_id}")
            return True
        return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        workflow = self.workflows.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = time.time()
            logger.info(f"Workflow cancelled: {workflow_id}")
            return True
        return False
    
    def list_workflows(self) -> List[Dict]:
        """List all workflows"""
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "status": w.status.value,
                "steps": len(w.steps),
                "created_at": w.created_at
            }
            for w in self.workflows.values()
        ]
