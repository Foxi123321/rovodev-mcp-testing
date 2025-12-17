"""AI-powered search engine for Knowledge Database"""
from typing import List, Dict, Any, Optional
import logging

# RovoDev MCP friendly - absolute import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase

logger = logging.getLogger(__name__)


class KnowledgeSearchEngine:
    """Advanced search engine with AI-powered capabilities"""
    
    def __init__(self, db: KnowledgeDatabase):
        self.db = db
    
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Perform intelligent search across all knowledge types
        
        Args:
            query: Search query
            filters: Optional filters (type, category, date range, etc.)
            limit: Max results per category
        
        Returns:
            Dict with categorized search results
        """
        results = self.db.search_knowledge(query, limit=limit)
        
        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)
        
        # Rank and sort results
        results = self._rank_results(results, query)
        
        return results
    
    def _apply_filters(self, results: Dict[str, List[Dict[str, Any]]], 
                      filters: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Apply filters to search results"""
        filtered = {}
        
        for category, items in results.items():
            filtered_items = items
            
            # Filter by type
            if 'type' in filters and category == 'code':
                filtered_items = [item for item in filtered_items 
                                if item.get('symbol_type') == filters['type']]
            
            # Filter by project
            if 'project' in filters and category == 'code':
                filtered_items = [item for item in filtered_items 
                                if item.get('project_name') == filters['project']]
            
            # Filter by success
            if 'success_only' in filters and filters['success_only']:
                if category == 'commands':
                    filtered_items = [item for item in filtered_items if item.get('success')]
            
            filtered[category] = filtered_items
        
        return filtered
    
    def _rank_results(self, results: Dict[str, List[Dict[str, Any]]], 
                     query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Rank and sort results by relevance"""
        # For now, results are already sorted by relevance from DB
        # Future: Add semantic similarity scoring
        return results
    
    def find_similar_code(self, code_snippet: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar code snippets (future: use embeddings)"""
        # For now, use text search on code snippets
        return self.db.query_code_knowledge(code_snippet, limit=limit)
    
    def suggest_solutions(self, error_text: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Suggest solutions for an error with context"""
        solutions = self.db.get_error_solution(error_text, limit=5)
        
        # If context provided, filter/rank by context relevance
        if context and solutions:
            # Simple context matching for now
            solutions = sorted(solutions, 
                             key=lambda s: self._context_relevance(s.get('context', ''), context),
                             reverse=True)
        
        return solutions
    
    def _context_relevance(self, solution_context: str, query_context: str) -> float:
        """Calculate context relevance score (0-1)"""
        if not solution_context or not query_context:
            return 0.5
        
        # Simple word overlap scoring
        solution_words = set(solution_context.lower().split())
        query_words = set(query_context.lower().split())
        
        if not solution_words:
            return 0.5
        
        overlap = len(solution_words & query_words)
        return overlap / len(solution_words)
