"""
Knowledge DB Interface - Stores and retrieves execution patterns
"""
import sqlite3
import statistics
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class ExecutionRecord:
    """Record of a command execution"""
    command_name: str
    full_command: str
    duration_ms: int
    cpu_avg_percent: float
    memory_avg_mb: float
    exit_code: int
    success: bool
    timestamp: str
    notes: str = ""

@dataclass
class CommandBaseline:
    """Baseline statistics for a command"""
    command_pattern: str
    avg_duration_ms: float
    std_dev_ms: float
    min_duration_ms: int
    max_duration_ms: int
    sample_count: int
    last_updated: str

class KnowledgeDBInterface:
    """Interface to Knowledge Database for storing execution patterns"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".rovodev" / "knowledge_db" / "knowledge.db")
        
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables if they don't exist"""
        cursor = self.connection.cursor()
        
        # AI decisions table (for stuck process decisions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario TEXT NOT NULL,
                context TEXT,
                decision TEXT,
                outcome TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Command executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_name TEXT NOT NULL,
                full_command TEXT,
                duration_ms INTEGER,
                cpu_avg_percent REAL,
                memory_avg_mb REAL,
                exit_code INTEGER,
                success BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Process baselines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS process_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_pattern TEXT UNIQUE NOT NULL,
                avg_duration_ms REAL,
                std_dev_ms REAL,
                min_duration_ms INTEGER,
                max_duration_ms INTEGER,
                sample_count INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Stuck alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stuck_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pid INTEGER,
                process_name TEXT,
                command TEXT,
                alert_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                ai_confidence REAL,
                resolved BOOLEAN DEFAULT 0
            )
        """)
        
        self.connection.commit()
        print("✅ Knowledge DB tables ready")
    
    def store_execution(self, record: ExecutionRecord) -> int:
        """Store a command execution record"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO command_executions (
                command_name, full_command, duration_ms, cpu_avg_percent,
                memory_avg_mb, exit_code, success, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.command_name,
            record.full_command,
            record.duration_ms,
            record.cpu_avg_percent,
            record.memory_avg_mb,
            record.exit_code,
            record.success,
            record.notes
        ))
        
        self.connection.commit()
        
        # Update baseline
        self._update_baseline(record.command_name)
        
        return cursor.lastrowid
    
    def _update_baseline(self, command_name: str):
        """Recalculate baseline statistics for a command"""
        cursor = self.connection.cursor()
        
        # Get all executions for this command
        cursor.execute("""
            SELECT duration_ms FROM command_executions
            WHERE command_name = ? AND duration_ms IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 100
        """, (command_name,))
        
        durations = [row['duration_ms'] for row in cursor.fetchall()]
        
        if len(durations) < 2:
            return  # Need at least 2 samples for std dev
        
        avg = statistics.mean(durations)
        std_dev = statistics.stdev(durations)
        min_dur = min(durations)
        max_dur = max(durations)
        count = len(durations)
        
        # Upsert baseline
        cursor.execute("""
            INSERT INTO process_baselines (
                command_pattern, avg_duration_ms, std_dev_ms,
                min_duration_ms, max_duration_ms, sample_count, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(command_pattern) DO UPDATE SET
                avg_duration_ms = excluded.avg_duration_ms,
                std_dev_ms = excluded.std_dev_ms,
                min_duration_ms = excluded.min_duration_ms,
                max_duration_ms = excluded.max_duration_ms,
                sample_count = excluded.sample_count,
                last_updated = CURRENT_TIMESTAMP
        """, (command_name, avg, std_dev, min_dur, max_dur, count))
        
        self.connection.commit()
        print(f"📊 Updated baseline for '{command_name}': {avg/1000:.1f}s avg (±{std_dev/1000:.1f}s)")
    
    def get_baseline(self, command_name: str) -> Optional[CommandBaseline]:
        """Get baseline statistics for a command"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM process_baselines
            WHERE command_pattern = ?
        """, (command_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return CommandBaseline(
            command_pattern=row['command_pattern'],
            avg_duration_ms=row['avg_duration_ms'],
            std_dev_ms=row['std_dev_ms'],
            min_duration_ms=row['min_duration_ms'],
            max_duration_ms=row['max_duration_ms'],
            sample_count=row['sample_count'],
            last_updated=row['last_updated']
        )
    
    def store_alert(self, pid: int, process_name: str, command: str, 
                    reason: str, confidence: float) -> int:
        """Store a stuck process alert"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO stuck_alerts (
                pid, process_name, command, reason, ai_confidence
            ) VALUES (?, ?, ?, ?, ?)
        """, (pid, process_name, command, reason, confidence))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved"""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE stuck_alerts SET resolved = 1 WHERE id = ?
        """, (alert_id,))
        self.connection.commit()
    
    def get_recent_executions(self, command_name: str, limit: int = 10) -> List[Dict]:
        """Get recent executions for a command"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM command_executions
            WHERE command_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (command_name, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def store_decision(self, scenario: str, context: str, decision: str, outcome: str) -> int:
        """Store an AI decision for future reference"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO ai_decisions (scenario, context, decision, outcome)
            VALUES (?, ?, ?, ?)
        """, (scenario, context, decision, outcome))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def search_decisions(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar past decisions"""
        cursor = self.connection.cursor()
        
        # Simple text search - could be enhanced with vector similarity
        cursor.execute("""
            SELECT * FROM ai_decisions
            WHERE scenario LIKE ? OR context LIKE ? OR decision LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.connection.close()

# Test if run directly
if __name__ == "__main__":
    print("🧪 Testing Knowledge DB Interface...")
    
    db = KnowledgeDBInterface()
    
    # Test storing executions
    print("\n📝 Storing test execution...")
    record = ExecutionRecord(
        command_name="gradle build",
        full_command="gradle build --info",
        duration_ms=180000,  # 3 minutes
        cpu_avg_percent=65.0,
        memory_avg_mb=512.0,
        exit_code=0,
        success=True,
        timestamp=datetime.now().isoformat(),
        notes="Test execution"
    )
    
    exec_id = db.store_execution(record)
    print(f"✅ Stored execution ID: {exec_id}")
    
    # Store another one
    record2 = ExecutionRecord(
        command_name="gradle build",
        full_command="gradle build --info",
        duration_ms=175000,  # 2:55
        cpu_avg_percent=68.0,
        memory_avg_mb=520.0,
        exit_code=0,
        success=True,
        timestamp=datetime.now().isoformat(),
        notes="Test execution 2"
    )
    
    db.store_execution(record2)
    
    # Get baseline
    print("\n📊 Getting baseline...")
    baseline = db.get_baseline("gradle build")
    if baseline:
        print(f"   Command: {baseline.command_pattern}")
        print(f"   Average: {baseline.avg_duration_ms/1000:.1f}s")
        print(f"   Std Dev: {baseline.std_dev_ms/1000:.1f}s")
        print(f"   Samples: {baseline.sample_count}")
    
    db.close()
    print("\n✅ Knowledge DB Interface working!")
