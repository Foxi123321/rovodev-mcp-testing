"""Database manager for Knowledge Database MCP"""
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import logging

# RovoDev MCP friendly - absolute imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import DB_PATH, FTS_ENABLED
from models import (
    CodeFile, CodeKnowledge, CodeDependency,
    CommandPattern, CommandBaseline, SystemMetric,
    ErrorSolution, TroubleshootingLog, WebResearchCache
)

logger = logging.getLogger(__name__)


class KnowledgeDatabase:
    """Main database manager for the Knowledge Database"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database connection and schema"""
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Load and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        self.connection.executescript(schema_sql)
        self.connection.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    # ========================================================================
    # CODE INTELLIGENCE METHODS
    # ========================================================================
    
    def store_code_file(self, file: CodeFile) -> int:
        """Store or update a code file record"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO code_files (file_path, project_name, language, size_bytes, checksum, last_indexed)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                project_name = excluded.project_name,
                language = excluded.language,
                size_bytes = excluded.size_bytes,
                checksum = excluded.checksum,
                last_indexed = excluded.last_indexed
        """, (file.file_path, file.project_name, file.language, 
              file.size_bytes, file.checksum, datetime.now()))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def store_code_knowledge(self, knowledge: CodeKnowledge) -> int:
        """Store code knowledge entry"""
        cursor = self.connection.cursor()
        
        params_json = json.dumps(knowledge.parameters) if knowledge.parameters else None
        
        cursor.execute("""
            INSERT INTO code_knowledge 
            (file_id, symbol_name, symbol_type, line_start, line_end, 
             purpose, complexity, parameters, return_type, docstring, code_snippet)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (knowledge.file_id, knowledge.symbol_name, knowledge.symbol_type,
              knowledge.line_start, knowledge.line_end, knowledge.purpose,
              knowledge.complexity, params_json, knowledge.return_type,
              knowledge.docstring, knowledge.code_snippet))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def query_code_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query code knowledge using full-text search"""
        cursor = self.connection.cursor()
        
        if FTS_ENABLED:
            # Use FTS5 for fast text search
            cursor.execute("""
                SELECT ck.*, cf.file_path, cf.project_name
                FROM code_fts
                JOIN code_knowledge ck ON code_fts.rowid = ck.id
                JOIN code_files cf ON ck.file_id = cf.id
                WHERE code_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
        else:
            # Fallback to LIKE search
            cursor.execute("""
                SELECT ck.*, cf.file_path, cf.project_name
                FROM code_knowledge ck
                JOIN code_files cf ON ck.file_id = cf.id
                WHERE ck.symbol_name LIKE ? OR ck.purpose LIKE ? OR ck.purpose LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_code_dependencies(self, symbol_id: int, direction: str = "both") -> List[Dict[str, Any]]:
        """Get dependencies for a code symbol"""
        cursor = self.connection.cursor()
        
        if direction == "from":
            cursor.execute("""
                SELECT cd.*, ck.symbol_name as to_symbol_name
                FROM code_dependencies cd
                JOIN code_knowledge ck ON cd.to_symbol_id = ck.id
                WHERE cd.from_symbol_id = ?
            """, (symbol_id,))
        elif direction == "to":
            cursor.execute("""
                SELECT cd.*, ck.symbol_name as from_symbol_name
                FROM code_dependencies cd
                JOIN code_knowledge ck ON cd.from_symbol_id = ck.id
                WHERE cd.to_symbol_id = ?
            """, (symbol_id,))
        else:  # both
            cursor.execute("""
                SELECT 'outgoing' as direction, cd.*, ck.symbol_name as related_symbol
                FROM code_dependencies cd
                JOIN code_knowledge ck ON cd.to_symbol_id = ck.id
                WHERE cd.from_symbol_id = ?
                UNION ALL
                SELECT 'incoming' as direction, cd.*, ck.symbol_name as related_symbol
                FROM code_dependencies cd
                JOIN code_knowledge ck ON cd.from_symbol_id = ck.id
                WHERE cd.to_symbol_id = ?
            """, (symbol_id, symbol_id))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # COMMAND EXECUTION METHODS
    # ========================================================================
    
    def store_command_pattern(self, pattern: CommandPattern) -> int:
        """Store command execution record"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO command_patterns 
            (command, command_type, duration_ms, exit_code, cpu_avg, cpu_max,
             memory_peak_mb, disk_read_mb, disk_write_mb, network_sent_mb, network_recv_mb,
             success, output_snippet, error_snippet, working_directory, environment_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pattern.command, pattern.command_type, pattern.duration_ms,
              pattern.exit_code, pattern.cpu_avg, pattern.cpu_max,
              pattern.memory_peak_mb, pattern.disk_read_mb, pattern.disk_write_mb,
              pattern.network_sent_mb, pattern.network_recv_mb,
              pattern.success, pattern.output_snippet, pattern.error_snippet,
              pattern.working_directory, pattern.environment_hash))
        
        self.connection.commit()
        
        # Update baseline
        self._update_command_baseline(pattern.command)
        
        return cursor.lastrowid
    
    def _update_command_baseline(self, command: str):
        """Update baseline statistics for a command"""
        cursor = self.connection.cursor()
        
        # Calculate statistics from recent executions
        cursor.execute("""
            SELECT 
                COUNT(*) as sample_count,
                AVG(duration_ms) as avg_duration,
                MIN(duration_ms) as min_duration,
                MAX(duration_ms) as max_duration,
                AVG(cpu_avg) as avg_cpu,
                AVG(memory_peak_mb) as avg_memory,
                AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                (SELECT exit_code FROM command_patterns WHERE command = ? AND success = 1 
                 ORDER BY executed_at DESC LIMIT 1) as typical_exit_code
            FROM command_patterns
            WHERE command = ?
        """, (command, command))
        
        stats = cursor.fetchone()
        
        if stats and stats['sample_count'] > 0:
            # Calculate standard deviation
            cursor.execute("""
                SELECT 
                    SQRT(AVG((duration_ms - ?) * (duration_ms - ?))) as stddev
                FROM command_patterns
                WHERE command = ?
            """, (stats['avg_duration'], stats['avg_duration'], command))
            
            stddev = cursor.fetchone()['stddev'] or 0
            
            # Calculate confidence based on sample size
            confidence = min(1.0, stats['sample_count'] / 10.0)
            
            # Insert or update baseline
            cursor.execute("""
                INSERT INTO command_baselines 
                (command, sample_count, avg_duration_ms, stddev_duration_ms,
                 min_duration_ms, max_duration_ms, avg_cpu, avg_memory_mb,
                 typical_exit_code, success_rate, confidence, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(command) DO UPDATE SET
                    sample_count = excluded.sample_count,
                    avg_duration_ms = excluded.avg_duration_ms,
                    stddev_duration_ms = excluded.stddev_duration_ms,
                    min_duration_ms = excluded.min_duration_ms,
                    max_duration_ms = excluded.max_duration_ms,
                    avg_cpu = excluded.avg_cpu,
                    avg_memory_mb = excluded.avg_memory_mb,
                    typical_exit_code = excluded.typical_exit_code,
                    success_rate = excluded.success_rate,
                    confidence = excluded.confidence,
                    last_updated = excluded.last_updated
            """, (command, stats['sample_count'], int(stats['avg_duration']), stddev,
                  stats['min_duration'], stats['max_duration'], stats['avg_cpu'],
                  stats['avg_memory'], stats['typical_exit_code'], stats['success_rate'],
                  confidence, datetime.now()))
            
            self.connection.commit()
    
    def get_command_baseline(self, command: str) -> Optional[Dict[str, Any]]:
        """Get baseline statistics for a command"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM command_baselines WHERE command = ?", (command,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def store_system_metric(self, metric: SystemMetric):
        """Store a system metric measurement"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO system_metrics (metric_name, metric_value, unit, category)
            VALUES (?, ?, ?, ?)
        """, (metric.metric_name, metric.metric_value, metric.unit, metric.category))
        self.connection.commit()
    
    def get_system_baseline(self) -> Dict[str, Any]:
        """Get system baseline metrics"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                category,
                metric_name,
                AVG(metric_value) as avg_value,
                MIN(metric_value) as min_value,
                MAX(metric_value) as max_value,
                unit
            FROM system_metrics
            WHERE recorded_at > datetime('now', '-7 days')
            GROUP BY category, metric_name
        """)
        
        baseline = {}
        for row in cursor.fetchall():
            category = row['category']
            if category not in baseline:
                baseline[category] = {}
            baseline[category][row['metric_name']] = {
                'avg': row['avg_value'],
                'min': row['min_value'],
                'max': row['max_value'],
                'unit': row['unit']
            }
        
        return baseline
    
    # ========================================================================
    # ERROR SOLUTION METHODS
    # ========================================================================
    
    def store_error_solution(self, solution: ErrorSolution) -> int:
        """Store an error solution"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO error_solutions 
            (error_pattern, error_type, solution, context, command_context,
             success_count, failure_count, confidence, source, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (solution.error_pattern, solution.error_type, solution.solution,
              solution.context, solution.command_context, solution.success_count,
              solution.failure_count, solution.confidence, solution.source,
              solution.source_url))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_error_solution(self, error_pattern: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find solutions for an error pattern"""
        cursor = self.connection.cursor()
        
        if FTS_ENABLED:
            cursor.execute("""
                SELECT es.*
                FROM error_fts
                JOIN error_solutions es ON error_fts.rowid = es.id
                WHERE error_fts MATCH ?
                ORDER BY es.confidence DESC, es.success_count DESC
                LIMIT ?
            """, (error_pattern, limit))
        else:
            cursor.execute("""
                SELECT * FROM error_solutions
                WHERE error_pattern LIKE ?
                ORDER BY confidence DESC, success_count DESC
                LIMIT ?
            """, (f"%{error_pattern}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_solution_feedback(self, solution_id: int, success: bool):
        """Update solution success/failure count"""
        cursor = self.connection.cursor()
        
        if success:
            cursor.execute("""
                UPDATE error_solutions 
                SET success_count = success_count + 1,
                    last_used = ?,
                    confidence = (success_count + 1.0) / (success_count + failure_count + 2.0)
                WHERE id = ?
            """, (datetime.now(), solution_id))
        else:
            cursor.execute("""
                UPDATE error_solutions 
                SET failure_count = failure_count + 1,
                    confidence = (success_count) / (success_count + failure_count + 2.0)
                WHERE id = ?
            """, (solution_id,))
        
        self.connection.commit()
    
    # ========================================================================
    # GENERAL SEARCH
    # ========================================================================
    
    def search_knowledge(self, query: str, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all knowledge types"""
        results = {
            'code': self.query_code_knowledge(query, limit=limit),
            'errors': self.get_error_solution(query, limit=limit),
            'commands': []
        }
        
        # Search command patterns
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM command_patterns
            WHERE command LIKE ? OR output_snippet LIKE ?
            ORDER BY executed_at DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        results['commands'] = [dict(row) for row in cursor.fetchall()]
        
        return results
