"""
Utility functions for the application
"""

import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> dict:
    """
    Validate password strength
    Returns dict with is_valid and messages
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain a number")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def format_timestamp(timestamp: float) -> str:
    """Format unix timestamp to readable string"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_username(username: str) -> str:
    """Remove special characters from username"""
    return re.sub(r'[^a-zA-Z0-9_]', '', username)

class RateLimiter:
    """Generic rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        import time
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        self.requests[key].append(now)
        return True
