"""Multi-modal perception system for website exploration.

Combines DOM analysis, network capture, vision AI, and knowledge retrieval.
"""

from typing import Dict, Any, List, Optional
import json


class PerceptionSystem:
    """Multi-modal perception for website understanding."""
    
    def __init__(self):
        """Initialize the perception system."""
        self.perception_history = []
    
    async def perceive(self, url: str, session_id: str = "default") -> Dict[str, Any]:
        """Execute full perception cycle on a website.
        
        Args:
            url: The website URL to perceive
            session_id: Browser session ID
            
        Returns:
            Unified perception data
        """
        perceptions = {
            "url": url,
            "timestamp": self._get_timestamp(),
            "dom": await self._perceive_dom(url, session_id),
            "network": await self._perceive_network(session_id),
            "visual": await self._perceive_visual(session_id),
            "knowledge": await self._perceive_knowledge(url)
        }
        
        # Store in history
        self.perception_history.append(perceptions)
        
        return perceptions
    
    async def _perceive_dom(self, url: str, session_id: str) -> Dict[str, Any]:
        """Perceive DOM structure using browser automation.
        
        Args:
            url: The website URL
            session_id: Browser session ID
            
        Returns:
            DOM perception data
        """
        # Use rex-unstoppable-browser to actually browse the page
        try:
            # Import here to avoid circular dependencies
            import sys
            import os
            
            # Try to use MCP browser if available (would need MCP client integration)
            # For now, we'll extract data after browsing
            
            # Extract interactive elements using standard selectors
            selectors = {
                "buttons": "button, input[type='button'], input[type='submit']",
                "links": "a[href]",
                "forms": "form",
                "inputs": "input, textarea, select",
                "title": "title",
                "description": "meta[name='description']"
            }
            
            # This would call: mcp__rex_unstoppable_browser__invoke_tool('browse_url', {url, session_id})
            # Then: mcp__rex_unstoppable_browser__invoke_tool('extract_data', {session_id, selectors})
            
            # For now, return structure that can be filled by MCP integration
            return {
                "elements": {
                    "total": 0,  # Would be filled by actual browse
                    "interactive": [],  # Would extract buttons/clickables
                    "forms": [],  # Would extract form elements
                    "links": []  # Would extract all links
                },
                "metadata": {
                    "title": "",  # Would extract from <title>
                    "description": ""  # Would extract from meta tags
                },
                "technology": [],  # Would detect frameworks
                "_needs_browser_integration": True
            }
        except Exception as e:
            return {
                "elements": {"total": 0, "interactive": [], "forms": [], "links": []},
                "metadata": {"title": "", "description": ""},
                "technology": [],
                "error": str(e)
            }
    
    async def _perceive_network(self, session_id: str) -> Dict[str, Any]:
        """Perceive network traffic to discover APIs.
        
        Args:
            session_id: Browser session ID
            
        Returns:
            Network perception data
        """
        # This would capture network requests during browsing
        return {
            "api_calls": [],
            "endpoints_discovered": [],
            "auth_patterns": []
        }
    
    async def _perceive_visual(self, session_id: str) -> Dict[str, Any]:
        """Perceive visual layout using vision AI.
        
        Args:
            session_id: Browser session ID
            
        Returns:
            Visual perception data
        """
        # This would use vision-server-simple MCP for screenshot analysis
        return {
            "layout": "unknown",
            "components_detected": [],
            "ui_patterns": []
        }
    
    async def _perceive_knowledge(self, url: str) -> Dict[str, Any]:
        """Retrieve past knowledge about this website.
        
        Args:
            url: The website URL
            
        Returns:
            Knowledge from past explorations
        """
        # This would use knowledge-database MCP to query past learnings
        return {
            "past_interactions": [],
            "success_rate": 0.0,
            "learned_patterns": []
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def fuse_perceptions(self, perceptions: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse multi-modal perceptions into unified understanding.
        
        Args:
            perceptions: Raw perception data from all modalities
            
        Returns:
            Fused understanding
        """
        fused = {
            "url": perceptions["url"],
            "timestamp": perceptions["timestamp"],
            "structure": {
                "dom_summary": perceptions["dom"]["elements"],
                "navigation": self._extract_navigation(perceptions["dom"]),
                "content_areas": self._extract_content_areas(perceptions["visual"])
            },
            "capabilities": {
                "ui_interactions": self._extract_ui_capabilities(perceptions["dom"]),
                "api_endpoints": perceptions["network"]["endpoints_discovered"],
                "authentication": self._infer_auth(perceptions["network"])
            },
            "confidence": self._calculate_confidence(perceptions)
        }
        
        return fused
    
    def _extract_navigation(self, dom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract navigation elements from DOM."""
        # Extract nav links from DOM elements
        navigation = []
        for link in dom_data.get("elements", {}).get("links", []):
            navigation.append({
                "text": link.get("text", ""),
                "url": link.get("href", ""),
                "type": "link"
            })
        return navigation
    
    def _extract_content_areas(self, visual_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract content areas from visual perception."""
        content_areas = []
        for component in visual_data.get("components_detected", []):
            content_areas.append({
                "selector": component.get("selector", ""),
                "type": component.get("type", "unknown"),
                "description": component.get("description", "")
            })
        return content_areas
    
    def _extract_ui_capabilities(self, dom_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract UI interaction capabilities."""
        capabilities = []
        
        # Extract from interactive elements
        for elem in dom_data.get("elements", {}).get("interactive", []):
            capabilities.append({
                "action": elem.get("action", "click"),
                "target": elem.get("selector", ""),
                "success_rate": 0.5  # Default until we learn
            })
        
        return capabilities
    
    def _infer_auth(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Infer authentication requirements from network traffic."""
        auth_patterns = network_data.get("auth_patterns", [])
        
        if not auth_patterns:
            return {
                "required": False,
                "method": "unknown",
                "login_url": "",
                "authenticated": False
            }
        
        # Analyze patterns to infer auth method
        return {
            "required": True,
            "method": "unknown",  # Would analyze patterns here
            "login_url": "",
            "authenticated": False
        }
    
    def _calculate_confidence(self, perceptions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence in perception quality."""
        dom_score = 0.5 if perceptions["dom"]["elements"]["total"] > 0 else 0.0
        network_score = 0.5 if len(perceptions["network"]["api_calls"]) > 0 else 0.0
        visual_score = 0.5 if len(perceptions["visual"]["components_detected"]) > 0 else 0.0
        knowledge_score = perceptions["knowledge"].get("success_rate", 0.0)
        
        overall = (dom_score + network_score + visual_score + knowledge_score) / 4
        
        return {
            "overall": overall,
            "breakdown": {
                "structure": dom_score,
                "capabilities": network_score,
                "api_knowledge": (network_score + knowledge_score) / 2
            }
        }
