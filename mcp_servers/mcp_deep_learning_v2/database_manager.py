"""
Auto-managed SQLite database for code intelligence
Stores analysis from both AIs, manages schemas, handles caching
"""

import sqlite3
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from config import DB_PATH, CACHE_ENABLED, CACHE_TTL

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Auto-managed database for code analysis storage"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        self._create_tables()
        logger.info(f"Database initialized at {self.db_path}")
    
    def _create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Files table - tracks indexed files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                language TEXT,
                size_bytes INTEGER,
                last_modified REAL,
                last_indexed REAL,
                content_hash TEXT,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Code entities table - functions, classes, etc.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                entity_type TEXT NOT NULL,  -- 'function', 'class', 'method', 'variable'
                name TEXT NOT NULL,
                signature TEXT,
                start_line INTEGER,
                end_line INTEGER,
                code_snippet TEXT,
                created_at REAL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            )
        """)
        
        # Analysis results table - stores AI analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                analysis_type TEXT NOT NULL,  -- 'technical', 'semantic', 'consensus'
                
                -- Primary AI (DeepSeek)
                primary_model TEXT,
                primary_summary TEXT,
                primary_details TEXT,  -- JSON
                primary_confidence REAL,
                
                -- Secondary AI (Qwen)
                secondary_model TEXT,
                secondary_summary TEXT,
                secondary_details TEXT,  -- JSON
                secondary_confidence REAL,
                
                -- Consensus
                consensus_summary TEXT,
                consensus_confidence REAL,
                agreement_score REAL,
                needs_review BOOLEAN DEFAULT 0,
                
                created_at REAL DEFAULT (strftime('%s', 'now')),
                updated_at REAL DEFAULT (strftime('%s', 'now')),
                
                FOREIGN KEY (entity_id) REFERENCES code_entities(id) ON DELETE CASCADE
            )
        """)
        
        # Dependencies table - tracks relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_entity_id INTEGER NOT NULL,
                to_entity_id INTEGER NOT NULL,
                dependency_type TEXT NOT NULL,  -- 'calls', 'imports', 'inherits', 'uses'
                created_at REAL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (from_entity_id) REFERENCES code_entities(id) ON DELETE CASCADE,
                FOREIGN KEY (to_entity_id) REFERENCES code_entities(id) ON DELETE CASCADE,
                UNIQUE(from_entity_id, to_entity_id, dependency_type)
            )
        """)
        
        # Query cache table - speeds up repeated queries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                query_text TEXT NOT NULL,
                result TEXT NOT NULL,  -- JSON
                created_at REAL DEFAULT (strftime('%s', 'now')),
                accessed_at REAL DEFAULT (strftime('%s', 'now')),
                access_count INTEGER DEFAULT 1
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON code_entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_file ON code_entities(file_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_entity ON analysis_results(entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deps_from ON dependencies(from_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deps_to ON dependencies(to_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON query_cache(query_hash)")
        
        self.conn.commit()
    
    def store_file(self, file_path: str, language: str, size_bytes: int, 
                   last_modified: float, content_hash: str) -> int:
        """Store or update file metadata"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO files (file_path, language, size_bytes, last_modified, last_indexed, content_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                language = excluded.language,
                size_bytes = excluded.size_bytes,
                last_modified = excluded.last_modified,
                last_indexed = excluded.last_indexed,
                content_hash = excluded.content_hash
        """, (file_path, language, size_bytes, last_modified, time.time(), content_hash))
        
        self.conn.commit()
        
        # Get the file ID
        cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
        return cursor.fetchone()[0]
    
    def store_entity(self, file_id: int, entity_type: str, name: str,
                     signature: str = None, start_line: int = None,
                     end_line: int = None, code_snippet: str = None) -> int:
        """Store code entity (function, class, etc.)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO code_entities (file_id, entity_type, name, signature, 
                                      start_line, end_line, code_snippet)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_id, entity_type, name, signature, start_line, end_line, code_snippet))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def store_analysis(self, entity_id: int, analysis_data: Dict[str, Any]) -> int:
        """Store AI analysis results"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis_results (
                entity_id, analysis_type,
                primary_model, primary_summary, primary_details, primary_confidence,
                secondary_model, secondary_summary, secondary_details, secondary_confidence,
                consensus_summary, consensus_confidence, agreement_score, needs_review
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entity_id,
            analysis_data.get("analysis_type", "general"),
            analysis_data.get("primary_model"),
            analysis_data.get("primary_summary"),
            json.dumps(analysis_data.get("primary_details", {})),
            analysis_data.get("primary_confidence", 0.0),
            analysis_data.get("secondary_model"),
            analysis_data.get("secondary_summary"),
            json.dumps(analysis_data.get("secondary_details", {})),
            analysis_data.get("secondary_confidence", 0.0),
            analysis_data.get("consensus_summary"),
            analysis_data.get("consensus_confidence", 0.0),
            analysis_data.get("agreement_score", 0.0),
            analysis_data.get("needs_review", False)
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_entity_analysis(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """Get latest analysis for an entity"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analysis_results
            WHERE entity_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (entity_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return dict(row)
    
    def search_entities(self, name: str = None, entity_type: str = None,
                       file_path: str = None) -> List[Dict[str, Any]]:
        """Search for code entities"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT e.*, f.file_path, f.language
            FROM code_entities e
            JOIN files f ON e.file_id = f.id
            WHERE 1=1
        """
        params = []
        
        if name:
            query += " AND e.name LIKE ?"
            params.append(f"%{name}%")
        
        if entity_type:
            query += " AND e.entity_type = ?"
            params.append(entity_type)
        
        if file_path:
            query += " AND f.file_path LIKE ?"
            params.append(f"%{file_path}%")
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_dependencies(self, entity_id: int, direction: str = "both") -> List[Dict[str, Any]]:
        """Get dependencies for an entity"""
        cursor = self.conn.cursor()
        
        if direction == "from" or direction == "both":
            cursor.execute("""
                SELECT d.*, e.name as to_name, e.entity_type as to_type
                FROM dependencies d
                JOIN code_entities e ON d.to_entity_id = e.id
                WHERE d.from_entity_id = ?
            """, (entity_id,))
            
            results = [dict(row) for row in cursor.fetchall()]
        
        if direction == "to" or direction == "both":
            cursor.execute("""
                SELECT d.*, e.name as from_name, e.entity_type as from_type
                FROM dependencies d
                JOIN code_entities e ON d.from_entity_id = e.id
                WHERE d.to_entity_id = ?
            """, (entity_id,))
            
            if direction == "both":
                results.extend([dict(row) for row in cursor.fetchall()])
            else:
                results = [dict(row) for row in cursor.fetchall()]
        
        return results
    
    def cache_query(self, query: str, result: Any) -> None:
        """Cache query result"""
        if not CACHE_ENABLED:
            return
        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO query_cache (query_hash, query_text, result)
            VALUES (?, ?, ?)
            ON CONFLICT(query_hash) DO UPDATE SET
                result = excluded.result,
                accessed_at = strftime('%s', 'now'),
                access_count = access_count + 1
        """, (query_hash, query, json.dumps(result)))
        
        self.conn.commit()
    
    def get_cached_query(self, query: str) -> Optional[Any]:
        """Get cached query result if not expired"""
        if not CACHE_ENABLED:
            return None
        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT result, created_at FROM query_cache
            WHERE query_hash = ?
        """, (query_hash,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check if cache is expired
        age = time.time() - row[1]
        if age > CACHE_TTL:
            return None
        
        # Update access time
        cursor.execute("""
            UPDATE query_cache
            SET accessed_at = strftime('%s', 'now'),
                access_count = access_count + 1
            WHERE query_hash = ?
        """, (query_hash,))
        self.conn.commit()
        
        return json.loads(row[0])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM code_entities")
        entity_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        analysis_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dependencies")
        dependency_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM query_cache")
        cache_count = cursor.fetchone()[0]
        
        return {
            "files": file_count,
            "entities": entity_count,
            "analyses": analysis_count,
            "dependencies": dependency_count,
            "cached_queries": cache_count
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Test the database
    db = DatabaseManager()
    print("Database initialized successfully!")
    print(f"Stats: {db.get_stats()}")
