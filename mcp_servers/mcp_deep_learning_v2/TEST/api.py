"""
API endpoints for the application
"""

from flask import Flask, request, jsonify
from auth import login, logout, UserManager
from database import get_session, create_user

app = Flask(__name__)
user_manager = UserManager()

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    
    result = login(username, password)
    
    if "error" in result:
        return jsonify(result), 401
    
    return jsonify(result), 200

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout endpoint"""
    session_id = request.headers.get('Session-ID')
    
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400
    
    logout(session_id)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/register', methods=['POST'])
def api_register():
    """User registration endpoint"""
    from auth import hash_password
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({"error": "Missing required fields"}), 400
    
    password_hash = hash_password(password)
    user_id = create_user(username, password_hash, email)
    
    return jsonify({"user_id": user_id, "message": "User created"}), 201

@app.route('/api/profile', methods=['GET'])
def api_profile():
    """Get user profile"""
    session_id = request.headers.get('Session-ID')
    
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 401
    
    session = get_session(session_id)
    
    if not session:
        return jsonify({"error": "Invalid session"}), 401
    
    user = user_manager.get_cached_user(session['username'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Don't return password hash
    user_data = {
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"]
    }
    
    return jsonify(user_data), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
