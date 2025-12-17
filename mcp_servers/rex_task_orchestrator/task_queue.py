"""
Rex Task Orchestrator - Task Queue System
Handles task scheduling, prioritization, and parallel execution
"""
import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from queue import PriorityQueue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class Task:
    priority: int = field(compare=True)
    task_id: str = field(compare=False)
    name: str = field(compare=False)
    function: Callable = field(compare=False, repr=False)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: dict = field(default_factory=dict, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    created_at: float = field(default_factory=time.time, compare=False)
    started_at: Optional[float] = field(default=None, compare=False)
    completed_at: Optional[float] = field(default=None, compare=False)
    result: Any = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    retries: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)


class TaskQueue:
    def __init__(self, max_parallel: int = 5):
        self.max_parallel = max_parallel
        self.queue = PriorityQueue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.running = False
        self._task_counter = 0
        
    def add_task(
        self,
        name: str,
        function: Callable,
        priority: TaskPriority = TaskPriority.NORMAL,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3
    ) -> str:
        """Add a task to the queue"""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{int(time.time())}"
        
        task = Task(
            priority=priority.value,
            task_id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            max_retries=max_retries
        )
        
        self.queue.put(task)
        logger.info(f"Task added: {task_id} - {name} (Priority: {priority.name})")
        return task_id
    
    async def execute_task(self, task: Task) -> Task:
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        self.active_tasks[task.task_id] = task
        
        logger.info(f"Executing task: {task.task_id} - {task.name}")
        
        try:
            # Check if function is async or sync
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args, **task.kwargs)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            duration = task.completed_at - task.started_at
            logger.info(f"Task completed: {task.task_id} in {duration:.2f}s")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            
            logger.error(f"Task failed: {task.task_id} - {e}")
            
            # Retry logic
            if task.retries < task.max_retries:
                task.retries += 1
                task.status = TaskStatus.PENDING
                logger.info(f"Retrying task: {task.task_id} (Attempt {task.retries}/{task.max_retries})")
                self.queue.put(task)
        
        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
        
        return task
    
    async def worker(self):
        """Worker to process tasks from queue"""
        while self.running:
            if not self.queue.empty() and len(self.active_tasks) < self.max_parallel:
                task = self.queue.get()
                asyncio.create_task(self.execute_task(task))
            else:
                await asyncio.sleep(0.1)
    
    async def start(self):
        """Start the task queue processor"""
        self.running = True
        logger.info(f"Task queue started (max_parallel={self.max_parallel})")
        await self.worker()
    
    def stop(self):
        """Stop the task queue processor"""
        self.running = False
        logger.info("Task queue stopped")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a task"""
        task = self.active_tasks.get(task_id) or self.completed_tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "priority": TaskPriority(task.priority).name,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error,
            "retries": task.retries
        }
    
    def get_all_tasks(self) -> Dict[str, List[Dict]]:
        """Get all tasks grouped by status"""
        pending = []
        active = []
        completed = []
        failed = []
        
        # Check queue for pending tasks
        temp_queue = []
        while not self.queue.empty():
            task = self.queue.get()
            temp_queue.append(task)
            pending.append(self.get_task_status(task.task_id))
        
        # Put tasks back
        for task in temp_queue:
            self.queue.put(task)
        
        # Active tasks
        for task in self.active_tasks.values():
            active.append(self.get_task_status(task.task_id))
        
        # Completed/Failed tasks
        for task in self.completed_tasks.values():
            if task.status == TaskStatus.COMPLETED:
                completed.append(self.get_task_status(task.task_id))
            elif task.status == TaskStatus.FAILED:
                failed.append(self.get_task_status(task.task_id))
        
        return {
            "pending": pending,
            "active": active,
            "completed": completed,
            "failed": failed
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        # Can only cancel pending tasks, not active ones
        temp_queue = []
        cancelled = False
        
        while not self.queue.empty():
            task = self.queue.get()
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                self.completed_tasks[task_id] = task
                cancelled = True
                logger.info(f"Task cancelled: {task_id}")
            else:
                temp_queue.append(task)
        
        for task in temp_queue:
            self.queue.put(task)
        
        return cancelled
