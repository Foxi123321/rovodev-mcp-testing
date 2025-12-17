"""Configuration for Knowledge Database MCP"""
import os
from pathlib import Path

# Database location
DB_DIR = Path.home() / ".rovodev" / "knowledge_db"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "knowledge.db"

# Search settings
FTS_ENABLED = False  # Disabled - using simple LIKE search
SEMANTIC_SEARCH_ENABLED = False  # Optional, requires embeddings

# Cache settings
QUERY_CACHE_SIZE = 1000
QUERY_CACHE_TTL = 3600  # 1 hour

# System baseline settings
BASELINE_SAMPLE_SIZE = 10  # Number of runs to establish baseline
BASELINE_CONFIDENCE_THRESHOLD = 0.8

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = DB_DIR / "knowledge_db.log"
