"""
Database operations for user and session management
"""

import sqlite3
from typing import Optional, Dict

DB_PATH = "users.db"

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def get_user(username: str) -> Optional[Dict]:
    """Retrieve user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "email": row[3],
            "created_at": row[4]
        }
    return None

def save_session(session_data: Dict):
    """Save session to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO sessions (session_id, username, created_at) VALUES (?, ?, ?)",
        (session_data["session_id"], session_data["username"], session_data["created_at"])
    )
    
    conn.commit()
    conn.close()

def delete_session(session_id: str):
    """Delete session from database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    
    conn.commit()
    conn.close()

def get_session(session_id: str) -> Optional[Dict]:
    """Get session by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "session_id": row[1],
            "username": row[2],
            "created_at": row[3]
        }
    return None

def create_user(username: str, password_hash: str, email: str) -> int:
    """Create a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
        (username, password_hash, email)
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id
