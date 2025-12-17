"""
Rex Task Orchestrator - Resource Monitor
Monitors system health: CPU, memory, disk, process tracking
"""
import psutil
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResourceSnapshot:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    process_count: int
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_gb": round(self.memory_used_gb, 2),
            "memory_total_gb": round(self.memory_total_gb, 2),
            "disk_percent": self.disk_percent,
            "disk_used_gb": round(self.disk_used_gb, 2),
            "disk_total_gb": round(self.disk_total_gb, 2),
            "process_count": self.process_count
        }


class ResourceMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.check_interval = config.get("check_interval_seconds", 30)
        self.cpu_threshold = config.get("cpu_threshold_percent", 85)
        self.memory_threshold = config.get("memory_threshold_percent", 90)
        self.disk_threshold = config.get("disk_threshold_percent", 95)
        self.enable_alerts = config.get("enable_alerts", True)
        
        self.history: List[ResourceSnapshot] = []
        self.max_history = 100
        self.alerts: List[Dict] = []
        self.running = False
    
    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get current system resource snapshot"""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        process_count = len(psutil.pids())
        
        snapshot = ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            disk_percent=disk_percent,
            disk_used_gb=disk_used_gb,
            disk_total_gb=disk_total_gb,
            process_count=process_count
        )
        
        return snapshot
    
    def check_thresholds(self, snapshot: ResourceSnapshot):
        """Check if any thresholds are exceeded"""
        alerts = []
        
        if snapshot.cpu_percent > self.cpu_threshold:
            alert = {
                "type": "cpu",
                "severity": "warning",
                "message": f"CPU usage at {snapshot.cpu_percent:.1f}% (threshold: {self.cpu_threshold}%)",
                "timestamp": snapshot.timestamp,
                "value": snapshot.cpu_percent,
                "threshold": self.cpu_threshold
            }
            alerts.append(alert)
            logger.warning(alert["message"])
        
        if snapshot.memory_percent > self.memory_threshold:
            alert = {
                "type": "memory",
                "severity": "warning",
                "message": f"Memory usage at {snapshot.memory_percent:.1f}% (threshold: {self.memory_threshold}%)",
                "timestamp": snapshot.timestamp,
                "value": snapshot.memory_percent,
                "threshold": self.memory_threshold
            }
            alerts.append(alert)
            logger.warning(alert["message"])
        
        if snapshot.disk_percent > self.disk_threshold:
            alert = {
                "type": "disk",
                "severity": "critical",
                "message": f"Disk usage at {snapshot.disk_percent:.1f}% (threshold: {self.disk_threshold}%)",
                "timestamp": snapshot.timestamp,
                "value": snapshot.disk_percent,
                "threshold": self.disk_threshold
            }
            alerts.append(alert)
            logger.critical(alert["message"])
        
        if self.enable_alerts and alerts:
            self.alerts.extend(alerts)
            # Keep only last 50 alerts
            self.alerts = self.alerts[-50:]
        
        return alerts
    
    def monitor_once(self) -> Dict:
        """Perform a single monitoring check"""
        snapshot = self.get_current_snapshot()
        
        # Add to history
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Check thresholds
        alerts = self.check_thresholds(snapshot)
        
        return {
            "snapshot": snapshot.to_dict(),
            "alerts": alerts,
            "status": "healthy" if not alerts else "warning"
        }
    
    def get_process_info(self, pid: Optional[int] = None) -> Dict:
        """Get detailed process information"""
        if pid:
            try:
                proc = psutil.Process(pid)
                return {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(interval=0.1),
                    "memory_percent": proc.memory_percent(),
                    "memory_mb": proc.memory_info().rss / (1024**2),
                    "create_time": proc.create_time(),
                    "num_threads": proc.num_threads()
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return {"error": f"Process {pid} not found or access denied"}
        else:
            # Get top processes by CPU/memory
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return {
                "top_processes": processes[:10],
                "total_processes": len(processes)
            }
    
    def get_history(self, last_n: int = 10) -> List[Dict]:
        """Get recent monitoring history"""
        return [s.to_dict() for s in self.history[-last_n:]]
    
    def get_alerts(self, last_n: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return self.alerts[-last_n:]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        logger.info("Alerts cleared")
    
    def get_summary(self) -> Dict:
        """Get overall system health summary"""
        snapshot = self.get_current_snapshot()
        
        status = "healthy"
        if (snapshot.cpu_percent > self.cpu_threshold or 
            snapshot.memory_percent > self.memory_threshold or 
            snapshot.disk_percent > self.disk_threshold):
            status = "warning"
        
        return {
            "status": status,
            "current": snapshot.to_dict(),
            "thresholds": {
                "cpu": self.cpu_threshold,
                "memory": self.memory_threshold,
                "disk": self.disk_threshold
            },
            "active_alerts": len([a for a in self.alerts if time.time() - a['timestamp'] < 300]),
            "total_alerts": len(self.alerts)
        }
