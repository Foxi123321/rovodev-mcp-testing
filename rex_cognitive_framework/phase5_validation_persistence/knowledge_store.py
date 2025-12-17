"""Knowledge storage and retrieval for learned patterns."""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class KnowledgeStore:
    """Stores and retrieves learned website intelligence patterns."""
    
    def __init__(self, storage_path: str = "knowledge_db"):
        """Initialize knowledge store.
        
        Args:
            storage_path: Path to store knowledge database
        """
        self.storage_path = storage_path
        self.memory = {
            "website_states": {},
            "exploration_patterns": [],
            "pivot_decisions": [],
            "success_stories": []
        }
    
    async def store_website_state(
        self,
        url: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store learned website state.
        
        Args:
            url: Website URL
            state: Complete website state
            
        Returns:
            Storage confirmation
        """
        state_id = self._generate_id(url)
        
        self.memory["website_states"][state_id] = {
            "url": url,
            "state": state,
            "stored_at": datetime.utcnow().isoformat() + "Z",
            "access_count": 0
        }
        
        # Would use knowledge-database MCP to persist
        return {
            "success": True,
            "state_id": state_id,
            "message": f"Stored state for {url}"
        }
    
    async def retrieve_website_state(
        self,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve learned website state.
        
        Args:
            url: Website URL
            
        Returns:
            Stored website state or None
        """
        state_id = self._generate_id(url)
        
        if state_id in self.memory["website_states"]:
            record = self.memory["website_states"][state_id]
            record["access_count"] += 1
            record["last_accessed"] = datetime.utcnow().isoformat() + "Z"
            return record["state"]
        
        # Would query knowledge-database MCP
        return None
    
    async def store_exploration_pattern(
        self,
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a successful exploration pattern.
        
        Args:
            pattern: Pattern details with strategy, actions, success rate
            
        Returns:
            Storage confirmation
        """
        pattern["stored_at"] = datetime.utcnow().isoformat() + "Z"
        pattern["pattern_id"] = self._generate_id(str(pattern))
        
        self.memory["exploration_patterns"].append(pattern)
        
        return {
            "success": True,
            "pattern_id": pattern["pattern_id"],
            "message": "Pattern stored successfully"
        }
    
    async def query_similar_patterns(
        self,
        query: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Query for similar exploration patterns.
        
        Args:
            query: Query parameters (goal_type, website_type, etc)
            limit: Maximum results
            
        Returns:
            List of matching patterns
        """
        # Simple keyword matching for now
        # Would use vector search in knowledge-database MCP
        
        results = []
        goal_type = query.get("goal_type", "")
        
        for pattern in self.memory["exploration_patterns"]:
            if goal_type and goal_type in str(pattern):
                results.append(pattern)
                if len(results) >= limit:
                    break
        
        return results
    
    async def store_success_story(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a complete success story (goal → exploration → result).
        
        Args:
            story: Complete story with goal, steps, outcome
            
        Returns:
            Storage confirmation
        """
        story["story_id"] = self._generate_id(str(story))
        story["stored_at"] = datetime.utcnow().isoformat() + "Z"
        
        self.memory["success_stories"].append(story)
        
        return {
            "success": True,
            "story_id": story["story_id"],
            "message": "Success story stored"
        }
    
    def _generate_id(self, data: str) -> str:
        """Generate a unique ID from data."""
        import hashlib
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge store statistics.
        
        Returns:
            Statistics about stored knowledge
        """
        return {
            "total_website_states": len(self.memory["website_states"]),
            "total_patterns": len(self.memory["exploration_patterns"]),
            "total_pivot_decisions": len(self.memory["pivot_decisions"]),
            "total_success_stories": len(self.memory["success_stories"]),
            "most_accessed_sites": self._get_most_accessed(5)
        }
    
    def _get_most_accessed(self, limit: int) -> List[Dict[str, Any]]:
        """Get most frequently accessed website states."""
        states = list(self.memory["website_states"].values())
        states.sort(key=lambda x: x.get("access_count", 0), reverse=True)
        
        return [
            {
                "url": s["url"],
                "access_count": s["access_count"],
                "last_accessed": s.get("last_accessed", "never")
            }
            for s in states[:limit]
        ]
