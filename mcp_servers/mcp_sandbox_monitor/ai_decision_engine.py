"""
AI Decision Engine - Determines if processes are stuck using local AI
"""
import requests
from typing import Tuple, Optional
from dataclasses import dataclass
from process_monitor import ProcessInfo
from knowledge_db_interface import KnowledgeDBInterface, CommandBaseline

@dataclass
class StuckDecision:
    """Decision about whether a process is stuck"""
    is_stuck: bool
    confidence: float  # 0.0 to 1.0
    reason: str
    recommendation: str
    ai_analysis: str = ""

class AIDecisionEngine:
    """Uses local AI to determine if processes are stuck"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "qwen3-coder:30b"  # Fast local model
        self.knowledge_db = KnowledgeDBInterface()
    
    def analyze_process(self, process: ProcessInfo) -> StuckDecision:
        """Analyze if a process is stuck"""
        
        # Get baseline from Knowledge DB
        baseline = self.knowledge_db.get_baseline(process.name)
        
        if not baseline:
            return StuckDecision(
                is_stuck=False,
                confidence=0.1,
                reason="No baseline data - cannot determine",
                recommendation="Let it run, collecting data for future analysis"
            )
        
        # Calculate deviation
        current_duration_ms = process.duration_seconds * 1000
        avg = baseline.avg_duration_ms
        std_dev = baseline.std_dev_ms
        
        deviation_factor = current_duration_ms / avg if avg > 0 else 0
        
        # Statistical analysis
        if current_duration_ms > (avg + 3 * std_dev):
            # Way over normal - DEFINITELY stuck
            reason = f"Running {deviation_factor:.1f}x normal time ({current_duration_ms/1000:.0f}s vs {avg/1000:.0f}s avg)"
            
            # Ask AI for confirmation
            ai_analysis = self._ask_ai_confirmation(process, baseline, current_duration_ms)
            
            return StuckDecision(
                is_stuck=True,
                confidence=0.95,
                reason=reason,
                recommendation="Kill and restart - process appears frozen",
                ai_analysis=ai_analysis
            )
        
        elif current_duration_ms > (avg + 2 * std_dev):
            # Possibly stuck - suspicious
            reason = f"Taking {deviation_factor:.1f}x normal time (avg {avg/1000:.0f}s)"
            
            ai_analysis = self._ask_ai_confirmation(process, baseline, current_duration_ms)
            
            return StuckDecision(
                is_stuck=False,  # Not definitive yet
                confidence=0.6,
                reason=reason,
                recommendation="Monitor closely - may be stuck or just a complex operation",
                ai_analysis=ai_analysis
            )
        
        else:
            # Within normal range
            return StuckDecision(
                is_stuck=False,
                confidence=0.9,
                reason=f"Within normal range ({current_duration_ms/1000:.0f}s, avg {avg/1000:.0f}s)",
                recommendation="Process is working normally"
            )
    
    def _ask_ai_confirmation(self, process: ProcessInfo, baseline: CommandBaseline, 
                            current_duration_ms: float) -> str:
        """Ask Qwen AI to analyze the situation"""
        
        prompt = f"""Analyze if this process is stuck:

Process: {process.name} (PID {process.pid})
Current duration: {current_duration_ms/1000:.0f} seconds
CPU usage: {process.cpu_percent:.1f}%
Memory: {process.memory_mb:.0f} MB

Historical baseline:
- Average duration: {baseline.avg_duration_ms/1000:.0f} seconds
- Std deviation: {baseline.std_dev_ms/1000:.0f} seconds
- Min/Max: {baseline.min_duration_ms/1000:.0f}s - {baseline.max_duration_ms/1000:.0f}s
- Samples: {baseline.sample_count}

Is this process stuck? Answer in 1-2 sentences with reasoning."""
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 200
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "AI analysis unavailable"
                
        except Exception as e:
            return f"AI error: {str(e)}"
    
    def quick_check(self, process_name: str, duration_seconds: float) -> str:
        """Quick check without full ProcessInfo"""
        baseline = self.knowledge_db.get_baseline(process_name)
        
        if not baseline:
            return f"⚪ {process_name}: No baseline data yet"
        
        current_ms = duration_seconds * 1000
        avg = baseline.avg_duration_ms
        std_dev = baseline.std_dev_ms
        
        if current_ms > (avg + 3 * std_dev):
            return f"🔴 {process_name}: STUCK ({current_ms/1000:.0f}s vs {avg/1000:.0f}s avg)"
        elif current_ms > (avg + 2 * std_dev):
            return f"🟡 {process_name}: Slow ({current_ms/1000:.0f}s vs {avg/1000:.0f}s avg)"
        else:
            return f"🟢 {process_name}: Normal ({current_ms/1000:.0f}s)"
    
    def close(self):
        """Close database connection"""
        self.knowledge_db.close()

# Test if run directly
if __name__ == "__main__":
    print("🧠 Testing AI Decision Engine...")
    
    engine = AIDecisionEngine()
    
    # Create a test process that's "stuck"
    print("\n🧪 Test 1: Simulating stuck gradle build...")
    test_process = ProcessInfo(
        pid=12345,
        name="gradle",
        cpu_percent=0.5,  # Low CPU = probably stuck
        memory_mb=512,
        start_time="2025-01-15 10:00:00",
        command_line="gradle build",
        duration_seconds=600  # 10 minutes (vs 3 min average)
    )
    
    # First store some baseline data
    from knowledge_db_interface import ExecutionRecord
    import datetime
    
    db = KnowledgeDBInterface()
    
    # Add normal gradle builds to baseline
    for dur in [175, 180, 185, 170, 190]:  # seconds
        record = ExecutionRecord(
            command_name="gradle",
            full_command="gradle build",
            duration_ms=dur * 1000,
            cpu_avg_percent=65.0,
            memory_avg_mb=512.0,
            exit_code=0,
            success=True,
            timestamp=datetime.datetime.now().isoformat(),
            notes="Baseline data"
        )
        db.store_execution(record)
    
    db.close()
    
    print("✅ Created baseline (avg ~180s)")
    
    # Now analyze the "stuck" process
    print("\n🔍 Analyzing process...")
    decision = engine.analyze_process(test_process)
    
    print(f"\n📊 Decision:")
    print(f"   Stuck: {decision.is_stuck}")
    print(f"   Confidence: {decision.confidence * 100:.0f}%")
    print(f"   Reason: {decision.reason}")
    print(f"   Recommendation: {decision.recommendation}")
    if decision.ai_analysis:
        print(f"   AI Analysis: {decision.ai_analysis}")
    
    # Test quick check
    print("\n🚀 Quick check:")
    result = engine.quick_check("gradle", 600)
    print(f"   {result}")
    
    engine.close()
    print("\n✅ AI Decision Engine working!")
