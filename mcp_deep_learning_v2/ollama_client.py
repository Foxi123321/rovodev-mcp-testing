"""
Ollama client for dual-AI analysis
Handles parallel calls to DeepSeek and Qwen models
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Tuple
import aiohttp

from config import (
    OLLAMA_BASE_URL,
    PRIMARY_MODEL,
    SECONDARY_MODEL,
    EMBEDDING_MODEL,
    OLLAMA_TIMEOUT,
    EMBEDDING_TIMEOUT,
    USE_DUAL_AI,
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_created = False
    
    def _ensure_session(self):
        """Ensure session exists (for non-context-manager usage)"""
        if self.session is None:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            self.session = aiohttp.ClientSession()
            self._session_created = True
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.1,
        timeout: int = OLLAMA_TIMEOUT
    ) -> Dict[str, Any]:
        """Generate completion from Ollama model"""
        self._ensure_session()  # Make sure we have a session
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with self.session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                return {
                    "model": model,
                    "response": result.get("response", ""),
                    "success": True,
                    "error": None
                }
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {model}")
            return {
                "model": model,
                "response": "",
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Error calling {model}: {e}")
            return {
                "model": model,
                "response": "",
                "success": False,
                "error": str(e)
            }
    
    async def get_embedding(
        self,
        text: str,
        model: str = EMBEDDING_MODEL
    ) -> Optional[list]:
        """Get embedding vector from Ollama"""
        url = f"{self.base_url}/api/embeddings"
        
        payload = {
            "model": model,
            "prompt": text
        }
        
        try:
            async with self.session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=EMBEDDING_TIMEOUT)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("embedding")
        
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    async def analyze_code_dual(
        self,
        code: str,
        context: str = "",
        technical_prompt: str = "",
        semantic_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Run dual AI analysis in parallel
        Returns results from both DeepSeek and Qwen
        """
        if not USE_DUAL_AI:
            # Single model mode
            result = await self.generate(
                model=PRIMARY_MODEL,
                prompt=technical_prompt.format(code=code, context=context)
            )
            return {
                "primary": result,
                "secondary": None,
                "mode": "single"
            }
        
        # Parallel execution of both models
        primary_task = self.generate(
            model=PRIMARY_MODEL,
            prompt=technical_prompt.format(code=code, context=context),
            system="You are a senior software engineer focused on technical analysis."
        )
        
        secondary_task = self.generate(
            model=SECONDARY_MODEL,
            prompt=semantic_prompt.format(code=code, context=context),
            system="You are a software architect focused on design and purpose."
        )
        
        primary_result, secondary_result = await asyncio.gather(
            primary_task,
            secondary_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(primary_result, Exception):
            logger.error(f"Primary model error: {primary_result}")
            primary_result = {
                "model": PRIMARY_MODEL,
                "response": "",
                "success": False,
                "error": str(primary_result)
            }
        
        if isinstance(secondary_result, Exception):
            logger.error(f"Secondary model error: {secondary_result}")
            secondary_result = {
                "model": SECONDARY_MODEL,
                "response": "",
                "success": False,
                "error": str(secondary_result)
            }
        
        return {
            "primary": primary_result,
            "secondary": secondary_result,
            "mode": "dual"
        }
    
    async def check_model_available(self, model: str) -> bool:
        """Check if a model is available in Ollama"""
        url = f"{self.base_url}/api/tags"
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                models = data.get("models", [])
                available = any(m.get("name") == model for m in models)
                
                if not available:
                    logger.warning(f"Model {model} not found in Ollama")
                
                return available
        
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False


async def test_ollama_connection():
    """Test connection to Ollama and check models"""
    async with OllamaClient() as client:
        print(f"Testing Ollama connection to {OLLAMA_BASE_URL}...")
        
        # Check primary model
        primary_available = await client.check_model_available(PRIMARY_MODEL)
        print(f"Primary model ({PRIMARY_MODEL}): {'✓ Available' if primary_available else '✗ Not found'}")
        
        # Check secondary model
        secondary_available = await client.check_model_available(SECONDARY_MODEL)
        print(f"Secondary model ({SECONDARY_MODEL}): {'✓ Available' if secondary_available else '✗ Not found'}")
        
        if primary_available:
            # Test generation
            print("\nTesting code analysis...")
            result = await client.generate(
                model=PRIMARY_MODEL,
                prompt="Explain what this Python function does: def add(a, b): return a + b",
                temperature=0.1
            )
            
            if result["success"]:
                print(f"✓ Analysis successful: {result['response'][:100]}...")
            else:
                print(f"✗ Analysis failed: {result['error']}")


if __name__ == "__main__":
    # Test the client
    asyncio.run(test_ollama_connection())
