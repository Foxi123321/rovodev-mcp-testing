"""
Vector Store - FAISS-based semantic search for code
Uses Ollama embeddings for vector representation
"""

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import asyncio

try:
    import numpy as np
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available - vector search disabled")

from config import VECTOR_INDEX_PATH, TOP_K_RESULTS, MIN_SIMILARITY_SCORE

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage FAISS vector index for semantic code search"""
    
    def __init__(self, index_path: Path = VECTOR_INDEX_PATH):
        self.index_path = index_path
        self.metadata_path = index_path.parent / f"{index_path.stem}_metadata.pkl"
        
        self.index: Optional[Any] = None
        self.metadata: List[Dict[str, Any]] = []
        self.dimension: Optional[int] = None
        
        if FAISS_AVAILABLE:
            self._load_or_create_index()
        else:
            logger.warning("Vector store disabled - FAISS not available")
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_path))
                self.dimension = self.index.d
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"Loaded vector index with {len(self.metadata)} entries")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self, dimension: int = 7168):
        """Create a new FAISS index"""
        if not FAISS_AVAILABLE:
            return
        
        self.dimension = dimension
        # Use IndexFlatIP for cosine similarity (after L2 normalization)
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata = []
        logger.info(f"Created new vector index with dimension {dimension}")
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    async def add_embedding(
        self,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> int:
        """
        Add a single embedding to the index
        Returns the ID of the added vector
        """
        if not FAISS_AVAILABLE or self.index is None:
            return -1
        
        if not embedding:
            logger.warning("Empty embedding provided, skipping")
            return -1
        
        # Convert to numpy array
        vector = np.array(embedding, dtype=np.float32)
        
        # Initialize index dimension if first entry
        if self.dimension is None:
            self._create_new_index(len(embedding))
        
        # Check dimension match
        if len(embedding) != self.dimension:
            logger.error(f"Embedding dimension {len(embedding)} doesn't match index dimension {self.dimension}")
            return -1
        
        # Normalize for cosine similarity
        vector = self._normalize_vector(vector)
        vector = vector.reshape(1, -1)
        
        # Add to FAISS index
        self.index.add(vector)
        
        # Store metadata
        vector_id = len(self.metadata)
        self.metadata.append(metadata)
        
        return vector_id
    
    async def add_batch(
        self,
        embeddings: List[List[float]],
        metadata_list: List[Dict[str, Any]]
    ) -> List[int]:
        """Add multiple embeddings at once (more efficient)"""
        if not FAISS_AVAILABLE or self.index is None:
            return []
        
        if len(embeddings) != len(metadata_list):
            raise ValueError("Embeddings and metadata must have same length")
        
        # Convert to numpy array
        vectors = np.array(embeddings, dtype=np.float32)
        
        # Initialize index dimension if first entry
        if self.dimension is None:
            self._create_new_index(vectors.shape[1])
        
        # Normalize all vectors
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        vectors = vectors / norms
        
        # Add to FAISS index
        start_id = len(self.metadata)
        self.index.add(vectors)
        
        # Store metadata
        self.metadata.extend(metadata_list)
        
        return list(range(start_id, start_id + len(embeddings)))
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = TOP_K_RESULTS,
        min_score: float = MIN_SIMILARITY_SCORE
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        Returns list of results with metadata and similarity scores
        """
        if not FAISS_AVAILABLE or self.index is None or len(self.metadata) == 0:
            return []
        
        # Convert to numpy array and normalize
        query_vector = np.array(query_embedding, dtype=np.float32)
        query_vector = self._normalize_vector(query_vector)
        query_vector = query_vector.reshape(1, -1)
        
        # Search
        k = min(top_k, len(self.metadata))
        distances, indices = self.index.search(query_vector, k)
        
        # Format results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            # FAISS IndexFlatIP returns inner product (cosine similarity after normalization)
            similarity = float(distance)
            
            # Filter by minimum score
            if similarity >= min_score:
                result = self.metadata[int(idx)].copy()
                result['similarity_score'] = similarity
                result['vector_id'] = int(idx)
                results.append(result)
        
        return results
    
    def save(self):
        """Save index and metadata to disk"""
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved vector index with {len(self.metadata)} entries")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def clear(self):
        """Clear the index"""
        if not FAISS_AVAILABLE:
            return
        
        self._create_new_index(self.dimension or 768)
        
        # Delete files
        if self.index_path.exists():
            self.index_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()
        
        logger.info("Cleared vector index")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not FAISS_AVAILABLE or self.index is None:
            return {
                "enabled": False,
                "total_vectors": 0
            }
        
        return {
            "enabled": True,
            "total_vectors": len(self.metadata),
            "dimension": self.dimension,
            "index_size_mb": self.index_path.stat().st_size / (1024 * 1024) if self.index_path.exists() else 0
        }


class CodeEmbedder:
    """Helper class to create embeddings using Ollama"""
    
    def __init__(self, ollama_client):
        self.client = ollama_client
    
    async def embed_code(self, code: str, context: str = "") -> Optional[List[float]]:
        """Create embedding for code snippet"""
        # Combine code and context
        text = f"{context}\n\n{code}" if context else code
        
        # Get embedding from Ollama
        embedding = await self.client.get_embedding(text)
        return embedding
    
    async def embed_batch(
        self,
        code_list: List[str],
        context_list: List[str] = None
    ) -> List[Optional[List[float]]]:
        """Create embeddings for multiple code snippets"""
        if context_list is None:
            context_list = [""] * len(code_list)
        
        # Create tasks for parallel processing
        tasks = [
            self.embed_code(code, context)
            for code, context in zip(code_list, context_list)
        ]
        
        # Execute in parallel
        embeddings = await asyncio.gather(*tasks)
        return embeddings


if __name__ == "__main__":
    # Test the vector store
    async def test():
        if not FAISS_AVAILABLE:
            print("FAISS not available - skipping test")
            return
        
        store = VectorStore()
        
        # Create some dummy embeddings (normally from Ollama)
        test_embeddings = [
            np.random.rand(768).tolist(),
            np.random.rand(768).tolist(),
            np.random.rand(768).tolist(),
        ]
        
        test_metadata = [
            {"name": "function1", "type": "function", "code": "def test(): pass"},
            {"name": "function2", "type": "function", "code": "def auth(): pass"},
            {"name": "class1", "type": "class", "code": "class User: pass"},
        ]
        
        # Add embeddings
        ids = await store.add_batch(test_embeddings, test_metadata)
        print(f"Added {len(ids)} vectors")
        
        # Search
        query = np.random.rand(768).tolist()
        results = await store.search(query, top_k=2)
        
        print(f"\nSearch results:")
        for result in results:
            print(f"  - {result['name']} (similarity: {result['similarity_score']:.2f})")
        
        # Stats
        print(f"\nStats: {store.get_stats()}")
        
        # Save
        store.save()
    
    asyncio.run(test())
