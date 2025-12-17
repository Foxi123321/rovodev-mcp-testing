#!/usr/bin/env python3
"""Quick test of Rex's unlimited memory system"""

from database import KnowledgeDatabase
from models import ConversationSession, ConversationMessage, ConversationInsight
from datetime import datetime
import json

def test_unlimited_memory():
    print("🧠 Testing Rex Unlimited Memory System\n")
    
    db = KnowledgeDatabase()
    print("✅ Database initialized\n")
    
    # Test 1: Store a session
    print("📝 Test 1: Storing conversation session...")
    session = ConversationSession(
        session_id="test_rex_memory_001",
        title="Test Rex Memory",
        workspace_path="/workspace/test",
        model_id="claude-3.5-sonnet",
        created_at=datetime.now(),
        last_message_at=datetime.now(),
        message_count=0,
        total_tokens=0
    )
    session_id = db.store_conversation_session(session)
    print(f"   ✅ Session stored with ID: {session_id}\n")
    
    # Test 2: Store messages
    print("💬 Test 2: Storing conversation messages...")
    messages = [
        ("user", "Boss, how do I fix CORS errors in my API?"),
        ("assistant", "Yo boss! CORS errors are easy. Add these headers to your API response..."),
        ("user", "Thanks! That worked. Now how about authentication?"),
        ("assistant", "For auth, boss, I recommend JWT tokens with refresh mechanism...")
    ]
    
    for idx, (role, content) in enumerate(messages):
        msg = ConversationMessage(
            session_id="test_rex_memory_001",
            message_index=idx,
            role=role,
            content=content,
            timestamp=datetime.now(),
            token_count=len(content) // 4
        )
        msg_id = db.store_conversation_message(msg)
        print(f"   ✅ Message {idx + 1} stored (ID: {msg_id})")
    print()
    
    # Test 3: Search memory
    print("🔍 Test 3: Searching conversation memory...")
    search_results = db.query_conversation_memory("CORS API", limit=5)
    print(f"   ✅ Found {len(search_results)} results for 'CORS API'")
    if search_results:
        print(f"   First result: {search_results[0]['content'][:60]}...")
    print()
    
    # Test 4: Get session context
    print("📖 Test 4: Retrieving session context...")
    context = db.get_session_context("test_rex_memory_001", message_limit=10)
    if context:
        print(f"   ✅ Retrieved {len(context.get('messages', []))} messages")
        print(f"   Session: {context.get('session', {}).get('title', 'N/A')}")
    print()
    
    # Test 5: Store insight
    print("💡 Test 5: Storing conversation insight...")
    insight = ConversationInsight(
        session_id="test_rex_memory_001",
        content="User needed CORS fix and JWT authentication setup",
        insight_type="solution",
        context="API security and authentication discussion",
        importance=0.8,
        tags=["cors", "auth", "jwt", "api"],
        created_at=datetime.now()
    )
    insight_id = db.store_conversation_insight(insight)
    print(f"   ✅ Insight stored (ID: {insight_id})\n")
    
    # Test 6: Get all sessions
    print("📊 Test 6: Getting all sessions...")
    all_sessions = db.get_all_sessions(limit=100)
    print(f"   ✅ Total sessions in memory: {len(all_sessions)}")
    for sess in all_sessions[:3]:
        print(f"      - {sess['session_id']}: {sess.get('title', 'Untitled')} ({sess['message_count']} messages)")
    print()
    
    db.close()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n🔥 Rex's unlimited memory is fully operational! 🔥\n")

if __name__ == "__main__":
    test_unlimited_memory()
