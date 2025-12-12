"""
Background Monitor Daemon - Autonomous Process Monitoring
Runs continuously, detects stuck processes, and handles them automatically
"""
import time
import threading
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from process_monitor import ProcessMonitor
from interactive_controller import InteractiveController
from ai_decision_engine import AIDecisionEngine
from knowledge_db_interface import KnowledgeDBInterface

@dataclass
class MonitoredProcess:
    """Information about a process being monitored"""
    pid: int
    name: str
    command: str
    start_time: float
    last_check_time: float
    stuck_detected: bool = False
    stuck_since: Optional[float] = None
    cpu_history: List[float] = None
    
    def __post_init__(self):
        if self.cpu_history is None:
            self.cpu_history = []

class BackgroundMonitor:
    """Autonomous background process monitor"""
    
    def __init__(self, check_interval: float = 2.0):
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None
        
        # Components
        self.process_monitor = ProcessMonitor()
        self.controller = InteractiveController()
        self.ai_engine = AIDecisionEngine()
        # Don't create knowledge_db here - will create in thread
        self.knowledge_db = None
        
        # Tracked processes
        self.tracked_processes: Dict[int, MonitoredProcess] = {}
        
        # Configuration
        self.stuck_threshold_seconds = 5  # Consider stuck after 5s of low CPU
        self.cpu_threshold = 2.0  # CPU % below this = idle
        self.min_threads_for_waiting = 2  # Need multiple threads to be "waiting"
        
        print("🤖 Background Monitor initialized")
        print(f"   Check interval: {check_interval}s")
        print(f"   Stuck threshold: {self.stuck_threshold_seconds}s")
        print(f"   CPU threshold: {self.cpu_threshold}%")
    
    def start(self):
        """Start the background monitoring daemon"""
        if self.running:
            print("⚠️  Monitor already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✅ Background monitor started")
        print("   Monitoring all PowerShell processes...")
    
    def stop(self):
        """Stop the background monitoring daemon"""
        if not self.running:
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # Don't close knowledge_db here - it's closed in the thread
        self.ai_engine.close()
        print("🛑 Background monitor stopped")
    
    def register_process(self, pid: int, command: str = ""):
        """Register a new process for monitoring"""
        proc_info = self.process_monitor.get_process_by_pid(pid)
        
        if proc_info:
            self.tracked_processes[pid] = MonitoredProcess(
                pid=pid,
                name=proc_info.name,
                command=command,
                start_time=time.time(),
                last_check_time=time.time()
            )
            print(f"📍 Registered PID {pid} for monitoring")
            return True
        else:
            print(f"⚠️  Cannot register PID {pid} - process not found")
            return False
    
    def unregister_process(self, pid: int):
        """Stop monitoring a process"""
        if pid in self.tracked_processes:
            del self.tracked_processes[pid]
            print(f"📍 Unregistered PID {pid}")
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)"""
        print("🔄 Monitor loop started")
        
        # Create knowledge DB connection in this thread
        self.knowledge_db = KnowledgeDBInterface()
        
        try:
            while self.running:
                try:
                    self._check_all_processes()
                    time.sleep(self.check_interval)
                except Exception as e:
                    print(f"❌ Error in monitor loop: {e}")
                    time.sleep(self.check_interval)
        finally:
            # Close DB in the same thread it was created
            if self.knowledge_db:
                self.knowledge_db.close()
                self.knowledge_db = None
    
    def _check_all_processes(self):
        """Check all tracked processes for stuck behavior"""
        current_time = time.time()
        
        # Check each tracked process
        pids_to_remove = []
        
        for pid, tracked in list(self.tracked_processes.items()):
            # Check if process still exists
            proc_info = self.process_monitor.get_process_by_pid(pid)
            
            if not proc_info:
                # Process ended
                print(f"✅ PID {pid} finished")
                pids_to_remove.append(pid)
                continue
            
            # Update tracking info
            tracked.last_check_time = current_time
            tracked.cpu_history.append(proc_info.cpu_percent)
            
            # Keep only last 10 samples
            if len(tracked.cpu_history) > 10:
                tracked.cpu_history.pop(0)
            
            # Check for stuck behavior
            runtime = current_time - tracked.start_time
            
            if runtime > self.stuck_threshold_seconds and not tracked.stuck_detected:
                if self._is_process_stuck(proc_info, tracked):
                    self._handle_stuck_process(pid, tracked, proc_info)
        
        # Clean up finished processes
        for pid in pids_to_remove:
            self.unregister_process(pid)
    
    def _is_process_stuck(self, proc_info, tracked: MonitoredProcess) -> bool:
        """Determine if a process is stuck/waiting for input"""
        # Check CPU usage (low = idle)
        if proc_info.cpu_percent > self.cpu_threshold:
            return False
        
        # Check if CPU has been consistently low
        if len(tracked.cpu_history) >= 3:
            avg_cpu = sum(tracked.cpu_history[-3:]) / 3
            if avg_cpu > self.cpu_threshold:
                return False
        
        # Additional check using psutil
        try:
            process = psutil.Process(proc_info.pid)
            num_threads = process.num_threads()
            
            # Waiting processes usually have multiple threads but low activity
            if num_threads < self.min_threads_for_waiting:
                return False
            
            return True
        except:
            return False
    
    def _handle_stuck_process(self, pid: int, tracked: MonitoredProcess, proc_info):
        """Handle a detected stuck process"""
        tracked.stuck_detected = True
        tracked.stuck_since = time.time()
        
        print("\n" + "=" * 70)
        print(f"🚨 STUCK PROCESS DETECTED!")
        print("=" * 70)
        print(f"📍 PID: {pid}")
        print(f"📝 Name: {proc_info.name}")
        print(f"⏱️  Runtime: {proc_info.duration_seconds:.0f}s")
        print(f"🔥 CPU: {proc_info.cpu_percent:.1f}%")
        print(f"💾 Memory: {proc_info.memory_mb:.0f}MB")
        print(f"📊 CPU History: {tracked.cpu_history}")
        print()
        
        # Analyze and decide
        print("🤖 Rex is analyzing the situation...")
        decision = self._make_decision(pid, tracked)
        
        if decision:
            print(f"✅ Decision: {decision['action']}")
            self._execute_decision(pid, decision)
        else:
            print("⚠️  No decision made - continuing to monitor")
        
        print("=" * 70)
        print()
    
    def _make_decision(self, pid: int, tracked: MonitoredProcess) -> Optional[Dict]:
        """Use AI to decide what to do with stuck process"""
        # Build context for AI
        context = {
            'pid': pid,
            'process_name': tracked.name,
            'command': tracked.command,
            'runtime': time.time() - tracked.start_time,
            'situation': 'Process appears to be waiting for user input',
            'indicators': [
                'Low CPU usage (< 2%)',
                'Multiple threads present',
                'No activity detected'
            ]
        }
        
        # Check knowledge DB first
        print("📚 Checking knowledge database for similar situations...")
        similar_cases = self.knowledge_db.search_decisions(
            query="stuck process waiting for input",
            limit=3
        )
        
        if similar_cases:
            print(f"   Found {len(similar_cases)} similar cases")
            # Could auto-apply previous decision if confidence is high
        else:
            print("   No similar cases found")
        
        # For now, default strategy: assume it's waiting for yes/no confirmation
        print("🎯 Default strategy: Assume waiting for Y/N confirmation")
        
        # In production, Rex would:
        # 1. Use AI to analyze the terminal output (OCR or access buffer)
        # 2. Identify the actual question being asked
        # 3. Check risk level
        # 4. Decide autonomously or ask boss
        
        decision = {
            'action': 'send_input',
            'input': 'Y',
            'reason': 'Common build/deployment confirmation pattern',
            'confidence': 0.7
        }
        
        return decision
    
    def _execute_decision(self, pid: int, decision: Dict):
        """Execute the decided action"""
        action = decision.get('action')
        
        if action == 'send_input':
            input_text = decision.get('input', 'Y')
            print(f"📝 Sending input: '{input_text}'")
            
            success = self.controller.answer_prompt(pid, input_text)
            
            if success:
                print("✅ Input sent successfully")
                
                # Log to knowledge DB
                self.knowledge_db.store_decision(
                    scenario="Stuck process waiting for input",
                    context=f"PID {pid}, sent '{input_text}'",
                    decision=decision.get('reason', 'Auto-response'),
                    outcome="Input sent"
                )
            else:
                print("❌ Failed to send input")
        
        elif action == 'kill':
            print(f"💀 Killing process {pid}")
            self.process_monitor.kill_process(pid)
        
        elif action == 'ignore':
            print(f"👁️  Ignoring - continuing to monitor")
        
        else:
            print(f"⚠️  Unknown action: {action}")
    
    def get_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'running': self.running,
            'tracked_processes': len(self.tracked_processes),
            'stuck_processes': sum(1 for p in self.tracked_processes.values() if p.stuck_detected),
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }
    
    def print_status(self):
        """Print current status to console"""
        status = self.get_status()
        
        print("\n" + "=" * 70)
        print("📊 BACKGROUND MONITOR STATUS")
        print("=" * 70)
        print(f"🔄 Running: {status['running']}")
        print(f"📍 Tracked Processes: {status['tracked_processes']}")
        print(f"🚨 Stuck Processes: {status['stuck_processes']}")
        
        if self.tracked_processes:
            print("\n📋 Monitored Processes:")
            for pid, tracked in self.tracked_processes.items():
                runtime = time.time() - tracked.start_time
                status_icon = "🚨" if tracked.stuck_detected else "✅"
                print(f"   {status_icon} PID {pid}: {tracked.name} (Runtime: {runtime:.0f}s)")
        
        print("=" * 70)
        print()


# Standalone test
if __name__ == "__main__":
    print("🎮 Testing Background Monitor Daemon")
    print("=" * 70)
    print()
    
    monitor = BackgroundMonitor(check_interval=1.0)
    monitor.start()
    
    # Test: Launch a process that will get stuck
    print("🧪 Launching test process that will get stuck...")
    
    test_script = """
    Write-Host '🔨 Starting work...'
    Start-Sleep -Seconds 2
    Write-Host '⚠️  Need confirmation!'
    $answer = Read-Host 'Continue? (Y/N)'
    Write-Host "You chose: $answer"
    Start-Sleep -Seconds 2
    """
    
    pid = monitor.controller.launch_monitored_process(test_script, visible=True)
    
    if pid:
        print(f"✅ Launched PID {pid}")
        monitor.register_process(pid, test_script)
        
        print("\n⏳ Monitoring for 30 seconds...")
        print("   Watch for automatic stuck detection and response!")
        print()
        
        try:
            for i in range(30):
                time.sleep(1)
                if i % 5 == 0:
                    monitor.print_status()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
    
    monitor.stop()
    print("\n✅ Test complete!")
