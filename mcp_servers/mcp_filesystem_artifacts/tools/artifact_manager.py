"""Artifact management with security controls."""
import asyncio
import json
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid


class ArtifactManager:
    """Manages artifacts with secure storage and retrieval."""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path).resolve()
        self.metadata_file = self.base_path / "artifacts_metadata.json"
        
        # Create subdirectories
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "screenshots").mkdir(exist_ok=True)
        (self.base_path / "logs").mkdir(exist_ok=True)
        (self.base_path / "reports").mkdir(exist_ok=True)
        (self.base_path / "test_results").mkdir(exist_ok=True)
        (self.base_path / "files").mkdir(exist_ok=True)
        (self.base_path / "other").mkdir(exist_ok=True)
        (self.base_path / "bundles").mkdir(exist_ok=True)
        
        # Load or initialize metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load artifact metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {"artifacts": {}, "bundles": {}}
        return {"artifacts": {}, "bundles": {}}
    
    def _save_metadata(self):
        """Save artifact metadata to disk."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _is_path_safe(self, file_path: str) -> bool:
        """Check if path is safe (within allowed directories)."""
        try:
            path = Path(file_path).resolve()
            # Must be within base_path or current working directory
            return (
                path.is_relative_to(self.base_path) or 
                path.is_relative_to(Path.cwd())
            )
        except:
            return False
    
    def _get_artifact_dir(self, artifact_type: str) -> Path:
        """Get directory for artifact type."""
        type_map = {
            "screenshot": "screenshots",
            "log": "logs",
            "test_result": "test_results",
            "report": "reports",
            "file": "files",
            "other": "other"
        }
        return self.base_path / type_map.get(artifact_type, "other")
    
    async def store_artifact(
        self,
        artifact_type: str,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store an artifact with metadata."""
        
        # Security check
        if not self._is_path_safe(file_path):
            return {"error": "File path not allowed (security restriction)"}
        
        source_path = Path(file_path).resolve()
        if not source_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # Generate unique artifact ID
        artifact_id = str(uuid.uuid4())
        
        # Determine destination
        dest_dir = self._get_artifact_dir(artifact_type)
        file_ext = source_path.suffix
        dest_path = dest_dir / f"{artifact_id}{file_ext}"
        
        # Copy file
        try:
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            return {"error": f"Failed to copy file: {str(e)}"}
        
        # Calculate file hash for integrity
        file_hash = self._calculate_hash(dest_path)
        
        # Store metadata
        artifact_metadata = {
            "id": artifact_id,
            "type": artifact_type,
            "original_path": str(source_path),
            "stored_path": str(dest_path),
            "file_size": dest_path.stat().st_size,
            "file_hash": file_hash,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        self.metadata["artifacts"][artifact_id] = artifact_metadata
        self._save_metadata()
        
        return {
            "status": "stored",
            "artifact_id": artifact_id,
            "stored_path": str(dest_path),
            "file_size": artifact_metadata["file_size"]
        }
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    async def retrieve_artifact(self, artifact_id: str) -> Dict[str, Any]:
        """Retrieve artifact metadata and path."""
        
        artifact = self.metadata["artifacts"].get(artifact_id)
        if not artifact:
            return {"error": f"Artifact not found: {artifact_id}"}
        
        # Verify file still exists
        stored_path = Path(artifact["stored_path"])
        if not stored_path.exists():
            return {"error": "Artifact file missing (may have been cleaned up)"}
        
        return {
            "artifact": artifact,
            "exists": True
        }
    
    async def list_artifacts(
        self,
        artifact_type: Optional[str] = None,
        execution_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List artifacts with optional filters."""
        
        artifacts = []
        
        for artifact_id, artifact in self.metadata["artifacts"].items():
            # Apply filters
            if artifact_type and artifact["type"] != artifact_type:
                continue
            
            if execution_id:
                meta_exec_id = artifact.get("metadata", {}).get("execution_id")
                if meta_exec_id != execution_id:
                    continue
            
            if tags:
                artifact_tags = artifact.get("metadata", {}).get("tags", [])
                if not any(tag in artifact_tags for tag in tags):
                    continue
            
            artifacts.append(artifact)
        
        return {
            "count": len(artifacts),
            "artifacts": artifacts
        }
    
    async def create_bundle(
        self,
        bundle_name: str,
        artifact_ids: List[str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a bundle of artifacts."""
        
        # Verify all artifacts exist
        missing = []
        for aid in artifact_ids:
            if aid not in self.metadata["artifacts"]:
                missing.append(aid)
        
        if missing:
            return {"error": f"Missing artifacts: {missing}"}
        
        bundle_id = str(uuid.uuid4())
        
        bundle_metadata = {
            "id": bundle_id,
            "name": bundle_name,
            "artifact_ids": artifact_ids,
            "created": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        self.metadata["bundles"][bundle_id] = bundle_metadata
        self._save_metadata()
        
        return {
            "status": "created",
            "bundle_id": bundle_id,
            "artifact_count": len(artifact_ids)
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get artifact statistics."""
        
        stats = {
            "total_artifacts": len(self.metadata["artifacts"]),
            "total_bundles": len(self.metadata["bundles"]),
            "by_type": {},
            "total_size_bytes": 0
        }
        
        for artifact in self.metadata["artifacts"].values():
            artifact_type = artifact["type"]
            stats["by_type"][artifact_type] = stats["by_type"].get(artifact_type, 0) + 1
            stats["total_size_bytes"] += artifact.get("file_size", 0)
        
        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        
        return stats
    
    async def cleanup_old_artifacts(
        self,
        days_old: int,
        artifact_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Remove old artifacts."""
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed = []
        
        for artifact_id, artifact in list(self.metadata["artifacts"].items()):
            # Check type filter
            if artifact_type and artifact["type"] != artifact_type:
                continue
            
            # Check age
            timestamp = datetime.fromisoformat(artifact["timestamp"])
            if timestamp < cutoff_date:
                # Remove file
                stored_path = Path(artifact["stored_path"])
                if stored_path.exists():
                    stored_path.unlink()
                
                # Remove metadata
                del self.metadata["artifacts"][artifact_id]
                removed.append(artifact_id)
        
        self._save_metadata()
        
        return {
            "status": "cleaned",
            "removed_count": len(removed),
            "removed_ids": removed
        }
    
    async def read_file_safe(
        self,
        file_path: str,
        max_size_kb: int = 1024
    ) -> Dict[str, Any]:
        """Safely read a file."""
        
        if not self._is_path_safe(file_path):
            return {"error": "File path not allowed"}
        
        path = Path(file_path).resolve()
        if not path.exists():
            return {"error": "File not found"}
        
        # Check size
        size_kb = path.stat().st_size / 1024
        if size_kb > max_size_kb:
            return {"error": f"File too large ({size_kb:.1f} KB > {max_size_kb} KB)"}
        
        # Read file
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "status": "success",
                "file_path": str(path),
                "content": content,
                "size_kb": round(size_kb, 2)
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    async def list_directory_safe(self, directory: str) -> Dict[str, Any]:
        """List directory contents."""
        
        if not self._is_path_safe(directory):
            return {"error": "Directory path not allowed"}
        
        path = Path(directory).resolve()
        if not path.exists():
            return {"error": "Directory not found"}
        
        if not path.is_dir():
            return {"error": "Not a directory"}
        
        try:
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "status": "success",
                "directory": str(path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}
