"""
Process Monitor - Watches PowerShell processes and tracks metrics
"""
import subprocess
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class ProcessInfo:
    """Information about a running process"""
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    start_time: str
    command_line: str
    duration_seconds: float

class ProcessMonitor:
    """Monitors system processes"""
    
    def __init__(self):
        self.tracked_processes: Dict[int, ProcessInfo] = {}
        self.process_history: List[ProcessInfo] = []
    
    def get_all_processes(self) -> List[ProcessInfo]:
        """Get all running processes with metrics"""
        try:
            # PowerShell command to get process info
            ps_command = """
            Get-Process | Where-Object {$_.ProcessName -notlike 'svchost*' -and $_.ProcessName -notlike 'System*'} | 
            Select-Object Id, ProcessName, CPU, @{Name='MemoryMB';Expression={[math]::Round($_.WorkingSet64/1MB, 2)}}, 
            StartTime, @{Name='Runtime';Expression={(New-TimeSpan -Start $_.StartTime).TotalSeconds}} |
            ConvertTo-Json -Compress
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            # Parse JSON output
            data = json.loads(result.stdout)
            
            # Handle single process (not array)
            if isinstance(data, dict):
                data = [data]
            
            processes = []
            for proc in data:
                try:
                    processes.append(ProcessInfo(
                        pid=proc.get('Id', 0),
                        name=proc.get('ProcessName', 'Unknown'),
                        cpu_percent=float(proc.get('CPU', 0) or 0),
                        memory_mb=float(proc.get('MemoryMB', 0) or 0),
                        start_time=proc.get('StartTime', ''),
                        command_line='',  # PowerShell doesn't easily give this
                        duration_seconds=float(proc.get('Runtime', 0) or 0)
                    ))
                except Exception as e:
                    continue
            
            return processes
            
        except Exception as e:
            print(f"Error getting processes: {e}")
            return []
    
    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Get specific process by PID"""
        try:
            ps_command = f"""
            $p = Get-Process -Id {pid} -ErrorAction SilentlyContinue
            if ($p) {{
                @{{
                    Id = $p.Id
                    ProcessName = $p.ProcessName
                    CPU = $p.CPU
                    MemoryMB = [math]::Round($p.WorkingSet64/1MB, 2)
                    StartTime = $p.StartTime.ToString()
                    Runtime = (New-TimeSpan -Start $p.StartTime).TotalSeconds
                }} | ConvertTo-Json -Compress
            }}
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return None
            
            data = json.loads(result.stdout)
            
            return ProcessInfo(
                pid=data['Id'],
                name=data['ProcessName'],
                cpu_percent=float(data.get('CPU', 0) or 0),
                memory_mb=float(data['MemoryMB']),
                start_time=data['StartTime'],
                command_line='',
                duration_seconds=float(data['Runtime'])
            )
            
        except Exception as e:
            return None
    
    def get_process_by_name(self, name: str) -> List[ProcessInfo]:
        """Get all processes matching name"""
        all_procs = self.get_all_processes()
        return [p for p in all_procs if name.lower() in p.name.lower()]
    
    def kill_process(self, pid: int) -> bool:
        """Kill a process by PID"""
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {pid} -Force"],
                capture_output=True,
                timeout=5
            )
            return True
        except:
            return False
    
    def is_process_alive(self, pid: int) -> bool:
        """Check if process is still running"""
        return self.get_process_by_pid(pid) is not None
    
    def to_dict(self, proc: ProcessInfo) -> dict:
        """Convert ProcessInfo to dict"""
        return asdict(proc)

# Test if run directly
if __name__ == "__main__":
    print("🔍 Testing Process Monitor...")
    monitor = ProcessMonitor()
    
    procs = monitor.get_all_processes()
    print(f"\n📊 Found {len(procs)} processes")
    
    # Show top 10 by CPU
    top_cpu = sorted(procs, key=lambda p: p.cpu_percent, reverse=True)[:10]
    print("\n🔥 Top 10 by CPU:")
    for p in top_cpu:
        print(f"   {p.name} (PID {p.pid}): {p.cpu_percent:.1f}% CPU, {p.memory_mb:.0f}MB")
    
    print("\n✅ Process Monitor working!")
