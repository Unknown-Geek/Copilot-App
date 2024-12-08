import pytest
from flask import session
import json
import sys
from pathlib import Path

# Add backend directory to path if needed
BACKEND_DIR = str(Path(__file__).parent.parent.absolute())
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

def test_security_configuration(client):
    """Test security configuration is properly set"""
    from server import create_app
    
    app = create_app(testing=True)
    
    assert app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds() == 3600  # 1 hour
    assert app.config['PERMANENT_SESSION_LIFETIME'].total_seconds() == 86400  # 1 day
    assert app.config['JWT_SECRET_KEY'] is not None
    assert app.secret_key is not None

def test_login_success(client):
    """Test successful login"""
    response = client.post('/login',
        json={'username': 'testuser', 'password': 'testpass'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'username' in data
    assert data['username'] == 'testuser'
    
    with client.session_transaction() as sess:
        assert sess['user_id'] == 'testuser'

def test_login_failure(client):
    """Test failed login attempts"""
    response = client.post('/login',
        json={'username': '', 'password': ''},
        content_type='application/json'
    )
    
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_protected_route(client):
    """Test protected route access"""
    # First login to get token
    login_response = client.post('/login',
        json={'username': 'testuser', 'password': 'testpass'},
        content_type='application/json'
    )
    token = json.loads(login_response.data)['access_token']
    
    # Test protected route with token
    response = client.get('/protected',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['logged_in_as'] == 'testuser'

def test_protected_route_no_token(client):
    """Test protected route without token"""
    response = client.get('/protected')
    assert response.status_code == 401

def test_rate_limiting(client):
    """Test rate limiting"""
    # Make 6 requests in quick succession
    for _ in range(6):
        response = client.post('/login',
            json={'username': 'testuser', 'password': 'testpass'},
            content_type='application/json'
        )
    # The 6th request should be rate limited
    assert response.status_code == 429

def test_logout(client):
    """Test logout functionality"""
    # First login
    client.post('/login',
        json={'username': 'testuser', 'password': 'testpass'},
        content_type='application/json'
    )
    
    # Then logout
    response = client.post('/logout')
    assert response.status_code == 200
    
    with client.session_transaction() as sess:
        assert 'user_id' not in sess