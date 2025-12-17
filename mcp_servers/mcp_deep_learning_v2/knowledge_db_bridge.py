"""
Bridge between Deep Learning MCP and Knowledge Database MCP
Syncs code analysis results to the shared knowledge database
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
import json

# Add knowledge DB to path
knowledge_db_path = Path(__file__).parent.parent / "mcp_knowledge_db"
sys.path.insert(0, str(knowledge_db_path))

# Import from knowledge_db with full module paths to avoid config conflicts
try:
    import importlib.util
    
    # Load database module
    db_spec = importlib.util.spec_from_file_location("kb_database", knowledge_db_path / "database.py")
    db_module = importlib.util.module_from_spec(db_spec)
    db_spec.loader.exec_module(db_module)
    KnowledgeDatabase = db_module.KnowledgeDatabase
    
    # Load models module
    models_spec = importlib.util.spec_from_file_location("kb_models", knowledge_db_path / "models.py")
    models_module = importlib.util.module_from_spec(models_spec)
    models_spec.loader.exec_module(models_module)
    CodeFile = models_module.CodeFile
    CodeKnowledge = models_module.CodeKnowledge
except Exception as e:
    print(f"⚠️  Failed to load knowledge DB modules: {e}")
    # Fallback - try direct import
    from database import KnowledgeDatabase
    from models import CodeFile, CodeKnowledge

class KnowledgeDBBridge:
    """Bridge to sync Deep Learning analysis to Knowledge DB"""
    
    def __init__(self):
        try:
            self.knowledge_db = KnowledgeDatabase()
            self.enabled = True
            print("✅ Knowledge DB Bridge: Connected")
        except Exception as e:
            print(f"⚠️  Knowledge DB Bridge: Failed to connect - {e}")
            self.enabled = False
    
    def calculate_file_hash(self, file_path: str, content: str = None) -> str:
        """Calculate hash of file content"""
        if content:
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except:
            return "unknown"
    
    def sync_file(self, file_path: str, language: str = None, size_bytes: int = None) -> Optional[int]:
        """Sync file metadata to Knowledge DB"""
        if not self.enabled:
            return None
        
        try:
            # Check if file already exists
            conn = self.knowledge_db.connection
            cursor = conn.execute("SELECT id FROM code_files WHERE file_path = ?", (file_path,))
            existing = cursor.fetchone()
            
            if existing:
                # File already exists, return existing ID
                return existing['id']
            
            # Insert new file
            code_file = CodeFile(
                file_path=file_path,
                project_name=self._extract_project_name(file_path),
                language=language or self._detect_language(file_path),
                size_bytes=size_bytes or self._get_file_size(file_path),
                checksum=self.calculate_file_hash(file_path)
            )
            
            file_id = self.knowledge_db.store_code_file(code_file)
            print(f"✅ Synced file to Knowledge DB (ID: {file_id})")
            return file_id
        except Exception as e:
            print(f"⚠️  Failed to sync file to Knowledge DB: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def sync_analysis(self, entity: Dict[str, Any], analysis_data: Dict[str, Any]) -> bool:
        """Sync code analysis results to Knowledge DB"""
        if not self.enabled:
            return False
        
        try:
            # First, ensure file exists in Knowledge DB
            file_id = self.sync_file(
                file_path=entity["file_path"],
                language=entity.get("language")
            )
            
            if not file_id:
                return False
            
            # Create CodeKnowledge entry
            code_knowledge = CodeKnowledge(
                file_id=file_id,
                symbol_name=entity["name"],
                symbol_type=entity["entity_type"],  # function, class, method
                line_start=entity.get("start_line"),
                line_end=entity.get("end_line"),
                purpose=analysis_data.get("consensus_summary", ""),
                complexity=self._determine_complexity(analysis_data),
                parameters=json.dumps(entity.get("parameters", [])),
                return_type=entity.get("return_type"),
                docstring=entity.get("docstring"),
                code_snippet=entity.get("code_snippet", "")
            )
            
            knowledge_id = self.knowledge_db.store_code_knowledge(code_knowledge)
            print(f"✅ Synced {entity['name']} to Knowledge DB (ID: {knowledge_id})")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to sync analysis to Knowledge DB: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_if_analyzed(self, file_path: str, file_hash: str, symbol_name: str) -> Optional[Dict[str, Any]]:
        """Check if this code has already been analyzed in Knowledge DB"""
        if not self.enabled:
            return None
        
        try:
            # Query Knowledge DB for existing analysis
            results = self.knowledge_db.query_code_knowledge(
                query=f'symbol_name:"{symbol_name}" AND file_path:"{file_path}"',
                limit=1
            )
            
            if results and len(results) > 0:
                # Check if file hasn't changed (using checksum)
                result = results[0]
                # TODO: Implement checksum comparison
                return result
            
            return None
        except Exception as e:
            print(f"⚠️  Failed to check Knowledge DB: {e}")
            return None
    
    def _extract_project_name(self, file_path: str) -> str:
        """Extract project name from file path"""
        path = Path(file_path)
        # Try to find a common project root indicator
        for parent in path.parents:
            if (parent / ".git").exists() or (parent / "package.json").exists():
                return parent.name
        
        # Fallback: use first directory after some common paths
        parts = path.parts
        for i, part in enumerate(parts):
            if part in ["src", "lib", "app", "code"]:
                if i > 0:
                    return parts[i-1]
        
        return "unknown"
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
        }
        return ext_map.get(ext, "unknown")
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except:
            return 0
    
    def _determine_complexity(self, analysis_data: Dict[str, Any]) -> str:
        """Determine complexity from analysis data"""
        # Use consensus confidence as a proxy
        confidence = analysis_data.get("consensus_confidence", 0.5)
        
        if confidence > 0.8:
            return "simple"
        elif confidence > 0.5:
            return "moderate"
        else:
            return "complex"
    
    def close(self):
        """Close Knowledge DB connection"""
        if self.enabled and hasattr(self, 'knowledge_db'):
            self.knowledge_db.close()


# Singleton instance
_bridge_instance = None

def get_bridge() -> KnowledgeDBBridge:
    """Get singleton bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = KnowledgeDBBridge()
    return _bridge_instance
