# backend/security.py
from flask import Blueprint, jsonify, session, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server import limiter  # Import the limiter instance from server
from datetime import timedelta
import secrets

# Create blueprint instead of app
security = Blueprint('security', __name__)

# Remove local limiter initialization since we're using the global one

# Security configuration moves to create_app()

# Remove global JWT and limiter instances since they should be initialized in app context

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
@security.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Simple validation for testing - in production would check against DB
    if username == 'testuser' and password == 'testpass':
        access_token = create_access_token(identity=username)
        session['user_id'] = username
        return jsonify({
            'access_token': access_token,
            'username': username
        }), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# Access control - protected route example
@security.route('/protected', methods=['GET']) 
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Logout endpoint
@security.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Successfully logged out"}), 200