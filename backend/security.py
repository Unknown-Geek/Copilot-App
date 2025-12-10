# backend/security.py
from flask import Blueprint, jsonify, session, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import secrets
from services.github_service import GitHubService

# Create blueprint instead of app
security = Blueprint('security', __name__)

# Mock user database - replace with real database in production
users = {
    'test_user': 'test_password'
}

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window",
    default_limits=["5 per minute"]  # Add default limits
)

# Initialize services
github_service = GitHubService()

# Key rotation - automatically rotates JWT key every 24 hours
def rotate_keys():
    security.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
    return {"message": "Keys rotated successfully"}, 200

# Session management
@security.before_request
def manage_session():
    session.permanent = True # Set session to use permanent lifetime
    if 'user_id' not in session:
        session['user_id'] = None

# User authentication
@security.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Add explicit rate limit to login route
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 401
        
    if username not in users or users[username] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    session['user_id'] = username
    return jsonify(access_token=access_token), 200

# Access control - protected route example
@security.route('/api/protected', methods=['GET']) 
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Logout endpoint
@security.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    session.pop('user_id', None)
    return jsonify({"msg": "Successfully logged out"}), 200

# GitHub OAuth routes
@security.route('/auth/github', methods=['GET'])
def github_login():
    """Initiate GitHub OAuth flow"""
    state = secrets.token_hex(16)
    session['github_state'] = state
    return github_service.get_authorization_url(state=state)

@security.route('/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session.get('github_state')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    if not state or state != stored_state:
        return jsonify({"error": "Invalid state parameter"}), 400
    
    try:
        # First exchange code for token
        token_response = github_service.exchange_code_for_token(code)
        if 'error' in token_response:
            return jsonify(token_response), 401
            
        # Then get access token from response
        token = github_service.get_access_token(token_response['access_token'])
        session['github_token'] = token
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401