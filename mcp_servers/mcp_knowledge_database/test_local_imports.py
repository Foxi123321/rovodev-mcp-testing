"""Test local imports"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase
print("Local imports work!")
