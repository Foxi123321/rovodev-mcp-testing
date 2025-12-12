"""
Configuration for Deep Learning Intelligence MCP Server v2
Auto-managed settings with sensible defaults
"""

import os
from pathlib import Path

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "qwen3-coder:30b")  # Using Qwen only (faster, works)
SECONDARY_MODEL = os.getenv("SECONDARY_MODEL", "qwen3-coder:30b")  # Not used in single mode
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-coder:30b")  # For vectors

# Analysis Configuration
USE_DUAL_AI = False  # Run both models in parallel (DISABLED - using Qwen only)
CONSENSUS_THRESHOLD = 0.75  # Agreement score to consider consensus reached
HIGH_CONFIDENCE_THRESHOLD = 0.85  # When to trust single model if other fails

# Timeout Settings
OLLAMA_TIMEOUT = 300  # seconds for analysis (increased for large models)
EMBEDDING_TIMEOUT = 30  # seconds for embeddings

# Database Configuration
DATA_DIR = Path(os.getenv("DEEP_LEARNING_DATA_DIR", Path.home() / ".rovodev" / "deep_learning_v2"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "knowledge.db"
VECTOR_INDEX_PATH = DATA_DIR / "vectors.faiss"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Knowledge DB compatibility (for bridge)
FTS_ENABLED = False
SEMANTIC_SEARCH_ENABLED = False

# Code Parsing Configuration
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.go': 'go',
    '.rs': 'rust',
}

# Documentation/Context files (indexed but not parsed for functions)
CONTEXT_EXTENSIONS = {
    '.json': 'json',
    '.md': 'markdown',
    '.html': 'html',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.txt': 'text',
    '.toml': 'toml',
    '.xml': 'xml',
}

# Ignore patterns for code indexing
IGNORE_PATTERNS = [
    '__pycache__',
    'node_modules',
    '.git',
    '.venv',
    'venv',
    'env',
    'dist',
    'build',
    '.eggs',
    '*.egg-info',
    '.pytest_cache',
    '.mypy_cache',
    'coverage',
    '.coverage',
    'htmlcov',
    '.next',
    'target',  # Rust
    'bin',
    'obj',  # C#
]

# Chunking Configuration
MAX_CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 100  # tokens

# Vector Search Configuration
TOP_K_RESULTS = 10  # Number of similar chunks to retrieve
MIN_SIMILARITY_SCORE = 0.6  # Minimum cosine similarity

# Cache Configuration
CACHE_ENABLED = True
CACHE_TTL = 86400  # 24 hours in seconds
MAX_CACHE_SIZE_MB = 500  # Auto-cleanup when exceeded

# Analysis Prompts (SHORT versions for speed)
TECHNICAL_ANALYSIS_PROMPT = """Analyze this code technically in 2-3 sentences:
1. What it does
2. Any issues or concerns

Code:
{code}

Context: {context}
"""

SEMANTIC_ANALYSIS_PROMPT = """Explain this code's purpose in 2-3 sentences:
1. What problem it solves
2. How it fits the system

Code:
{code}

Context: {context}
"""

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
