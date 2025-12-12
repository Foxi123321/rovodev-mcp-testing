"""
Authentication module for user management
"""

import hashlib
import time
from database import get_user, save_session

# Rate limiting storage
failed_attempts = {}

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_rate_limit(username: str) -> bool:
    """Check if user has exceeded rate limit (5 attempts per minute)"""
    if username not in failed_attempts:
        return True
    
    attempts = failed_attempts[username]
    recent_attempts = [t for t in attempts if time.time() - t < 60]
    
    if len(recent_attempts) >= 5:
        return False
    
    return True

def record_failed_attempt(username: str):
    """Record a failed login attempt"""
    if username not in failed_attempts:
        failed_attempts[username] = []
    failed_attempts[username].append(time.time())

def login(username: str, password: str) -> dict:
    """
    Authenticate user and create session
    Returns session data or None if authentication fails
    """
    # Check rate limit
    if not check_rate_limit(username):
        return {"error": "Too many failed attempts. Try again later."}
    
    # Get user from database
    user = get_user(username)
    
    if not user:
        record_failed_attempt(username)
        return {"error": "Invalid credentials"}
    
    # Verify password
    password_hash = hash_password(password)
    if user["password_hash"] != password_hash:
        record_failed_attempt(username)
        return {"error": "Invalid credentials"}
    
    # Create session
    session_id = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()
    session_data = {
        "session_id": session_id,
        "username": username,
        "created_at": time.time()
    }
    
    save_session(session_data)
    
    return session_data

def logout(session_id: str):
    """Invalidate a session"""
    from database import delete_session
    delete_session(session_id)

class UserManager:
    """Manages user operations"""
    
    def __init__(self):
        self.cache = {}
    
    def get_cached_user(self, username: str):
        """Get user from cache or database"""
        if username in self.cache:
            return self.cache[username]
        
        user = get_user(username)
        if user:
            self.cache[username] = user
        return user
    
    def clear_cache(self):
        """Clear the user cache"""
        self.cache = {}
