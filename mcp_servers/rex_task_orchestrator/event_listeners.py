"""
Rex Task Orchestrator - Event Listeners
Listen for file changes, git events, time triggers, and errors
"""
import os
import time
import logging
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Event:
    event_id: str
    event_type: str
    source: str
    data: Dict
    timestamp: float
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp
        }


class FileWatcherHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, callback: Callable, extensions: List[str]):
        self.callback = callback
        self.extensions = extensions
        self._event_counter = 0
    
    def _should_process(self, path: str) -> bool:
        """Check if file should be processed"""
        if not self.extensions:
            return True
        return any(path.endswith(ext) for ext in self.extensions)
    
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory and self._should_process(event.src_path):
            self._trigger_event("file_modified", event.src_path)
    
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory and self._should_process(event.src_path):
            self._trigger_event("file_created", event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory and self._should_process(event.src_path):
            self._trigger_event("file_deleted", event.src_path)
    
    def _trigger_event(self, event_type: str, file_path: str):
        """Trigger callback with event"""
        self._event_counter += 1
        event = Event(
            event_id=f"file_event_{self._event_counter}_{int(time.time())}",
            event_type=event_type,
            source="file_watcher",
            data={"file_path": file_path},
            timestamp=time.time()
        )
        
        logger.info(f"File event: {event_type} - {file_path}")
        self.callback(event)


class EventListeners:
    """
    Event listening system for:
    - File changes (watchdog)
    - Time-based triggers (schedule)
    - Git events (custom)
    - Error events (custom)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.watch_dirs = config.get("watch_directories", ["."])
        self.watch_extensions = config.get("watch_extensions", [])
        self.enable_file_watcher = config.get("enable_file_watcher", True)
        
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.observers: List[Observer] = []
        self.event_history: List[Event] = []
        self.running = False
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for an event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Handler registered for: {event_type}")
    
    def unregister_handler(self, event_type: str, handler: Callable):
        """Unregister a handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                logger.info(f"Handler unregistered for: {event_type}")
            except ValueError:
                pass
    
    def start_file_watcher(self):
        """Start watching files for changes"""
        if not self.enable_file_watcher:
            logger.info("File watcher disabled")
            return
        
        logger.info(f"Starting file watcher for: {self.watch_dirs}")
        
        for watch_dir in self.watch_dirs:
            if not os.path.exists(watch_dir):
                logger.warning(f"Watch directory does not exist: {watch_dir}")
                continue
            
            event_handler = FileWatcherHandler(
                callback=self._handle_event,
                extensions=self.watch_extensions
            )
            
            observer = Observer()
            observer.schedule(event_handler, watch_dir, recursive=True)
            observer.start()
            
            self.observers.append(observer)
        
        logger.info(f"File watcher started ({len(self.observers)} observers)")
    
    def stop_file_watcher(self):
        """Stop file watchers"""
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers = []
        logger.info("File watcher stopped")
    
    def schedule_task(self, cron_expression: str, task: Callable, task_name: str):
        """Schedule a time-based task"""
        # Simple scheduling - every N minutes/hours/days
        if "every" in cron_expression.lower():
            parts = cron_expression.lower().split()
            if len(parts) >= 2:
                interval = parts[0]
                unit = parts[1]
                
                if "minute" in unit:
                    schedule.every(int(interval)).minutes.do(task)
                elif "hour" in unit:
                    schedule.every(int(interval)).hours.do(task)
                elif "day" in unit:
                    schedule.every(int(interval)).days.do(task)
                
                logger.info(f"Scheduled task: {task_name} - {cron_expression}")
    
    def trigger_event(self, event_type: str, source: str, data: Dict):
        """Manually trigger an event"""
        event = Event(
            event_id=f"event_{int(time.time())}_{len(self.event_history)}",
            event_type=event_type,
            source=source,
            data=data,
            timestamp=time.time()
        )
        
        self._handle_event(event)
    
    def _handle_event(self, event: Event):
        """Handle an event by calling registered handlers"""
        self.event_history.append(event)
        
        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history.pop(0)
        
        # Call handlers for this event type
        handlers = self.event_handlers.get(event.event_type, [])
        handlers.extend(self.event_handlers.get("*", []))  # Wildcard handlers
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    def start(self):
        """Start all listeners"""
        self.running = True
        self.start_file_watcher()
        logger.info("Event listeners started")
    
    def stop(self):
        """Stop all listeners"""
        self.running = False
        self.stop_file_watcher()
        schedule.clear()
        logger.info("Event listeners stopped")
    
    def get_event_history(self, event_type: Optional[str] = None, last_n: int = 10) -> List[Dict]:
        """Get event history"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [e.to_dict() for e in events[-last_n:]]
    
    def get_event_stats(self) -> Dict:
        """Get event statistics"""
        if not self.event_history:
            return {"total_events": 0, "by_type": {}}
        
        by_type = {}
        for event in self.event_history:
            by_type[event.event_type] = by_type.get(event.event_type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "by_type": by_type,
            "active_handlers": sum(len(handlers) for handlers in self.event_handlers.values())
        }
