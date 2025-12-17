"""
Session Bridge - Auto-sync RovoDev sessions to Knowledge DB
Gives Rex unlimited memory by storing all conversations with embeddings
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from database import KnowledgeDatabase
from models import ConversationSession, ConversationMessage, ConversationInsight

logger = logging.getLogger(__name__)


class SessionMemoryBridge:
    """Bridge between RovoDev sessions and Knowledge DB for unlimited memory"""
    
    def __init__(self, db: KnowledgeDatabase):
        self.db = db
        self.embedding_cache = {}
    
    def sync_session_from_file(self, session_path: Path) -> bool:
        """Sync a RovoDev session file to the knowledge database"""
        try:
            # Load session context
            context_file = session_path / "session_context.json"
            if not context_file.exists():
                logger.warning(f"No session_context.json in {session_path}")
                return False
            
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            # Load metadata
            metadata_file = session_path / "metadata.json"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            session_id = context_data.get('id')
            if not session_id:
                logger.error(f"No session ID in {session_path}")
                return False
            
            # Extract session info
            message_history = context_data.get('message_history', [])
            
            # Create ConversationSession
            session = ConversationSession(
                session_id=session_id,
                title=metadata.get('title'),
                workspace_path=metadata.get('workspace_path'),
                model_id=context_data.get('model', {}).get('model_name') if isinstance(context_data.get('model'), dict) else context_data.get('model'),
                created_at=datetime.fromisoformat(metadata['created']) if 'created' in metadata else None,
                last_message_at=datetime.fromisoformat(metadata['last_saved']) if 'last_saved' in metadata else None,
                message_count=len(message_history),
                total_tokens=0,  # Will calculate
                is_active=True
            )
            
            # Store session
            self.db.store_conversation_session(session)
            
            # Store each message
            total_tokens = 0
            for idx, msg in enumerate(message_history):
                message = self._parse_message(session_id, idx, msg)
                if message:
                    self.db.store_conversation_message(message)
                    total_tokens += message.token_count or 0
            
            # Update total tokens
            session.total_tokens = total_tokens
            self.db.store_conversation_session(session)
            
            logger.info(f"✅ Synced session {session_id}: {len(message_history)} messages")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync session {session_path}: {e}")
            return False
    
    def _parse_message(self, session_id: str, index: int, msg: Dict[str, Any]) -> Optional[ConversationMessage]:
        """Parse a RovoDev message into ConversationMessage"""
        try:
            # Handle different message formats
            role = msg.get('role', 'unknown')
            
            # Extract content based on message structure
            content = ""
            if isinstance(msg.get('content'), str):
                content = msg['content']
            elif isinstance(msg.get('content'), list):
                # Handle parts-based content
                parts = msg['content']
                text_parts = [p.get('text', '') for p in parts if isinstance(p, dict) and 'text' in p]
                content = '\n'.join(text_parts)
            
            if not content:
                return None
            
            # Estimate token count (rough: ~4 chars per token)
            token_count = len(content) // 4
            
            # Get timestamp
            timestamp = None
            if 'timestamp' in msg:
                try:
                    timestamp = datetime.fromisoformat(msg['timestamp'])
                except:
                    pass
            
            message = ConversationMessage(
                session_id=session_id,
                message_index=index,
                role=role,
                content=content,
                timestamp=timestamp or datetime.now(),
                token_count=token_count,
                model_used=None,  # Not always available
                embedding=None  # Will be generated on demand
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to parse message {index}: {e}")
            return None
    
    def sync_all_sessions(self, sessions_dir: Path) -> Dict[str, int]:
        """Sync all RovoDev sessions to knowledge DB"""
        stats = {
            'total': 0,
            'synced': 0,
            'failed': 0,
            'skipped': 0
        }
        
        if not sessions_dir.exists():
            logger.warning(f"Sessions directory not found: {sessions_dir}")
            return stats
        
        # Get all session directories
        session_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
        stats['total'] = len(session_dirs)
        
        logger.info(f"🔄 Syncing {stats['total']} sessions to Knowledge DB...")
        
        for session_dir in session_dirs:
            try:
                if self.sync_session_from_file(session_dir):
                    stats['synced'] += 1
                else:
                    stats['skipped'] += 1
            except Exception as e:
                logger.error(f"Error syncing {session_dir}: {e}")
                stats['failed'] += 1
        
        logger.info(f"✅ Sync complete: {stats['synced']} synced, {stats['failed']} failed, {stats['skipped']} skipped")
        return stats
    
    def get_relevant_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant past conversations for context"""
        return self.db.query_conversation_memory(query, limit=limit)
    
    def extract_insights_from_session(self, session_id: str) -> int:
        """Extract key insights/decisions from a session using AI"""
        # TODO: Use Ollama to analyze conversation and extract insights
        # For now, return 0
        return 0


def sync_rovodev_sessions_to_memory():
    """Main function to sync all RovoDev sessions to unlimited memory"""
    from config import DB_PATH
    
    # Initialize DB
    db = KnowledgeDatabase(DB_PATH)
    bridge = SessionMemoryBridge(db)
    
    # Find RovoDev sessions directory
    sessions_dir = Path.home() / ".rovodev" / "sessions"
    
    if not sessions_dir.exists():
        print("❌ RovoDev sessions directory not found!")
        print(f"   Expected: {sessions_dir}")
        return
    
    print("🚀 Starting session sync to unlimited memory...")
    stats = bridge.sync_all_sessions(sessions_dir)
    
    print("\n📊 Sync Results:")
    print(f"   Total sessions: {stats['total']}")
    print(f"   ✅ Synced: {stats['synced']}")
    print(f"   ⚠️  Failed: {stats['failed']}")
    print(f"   ⏭️  Skipped: {stats['skipped']}")
    
    # Get session count
    sessions = db.get_all_sessions(limit=1000)
    print(f"\n💾 Knowledge DB now contains {len(sessions)} conversation sessions")
    
    db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_rovodev_sessions_to_memory()
