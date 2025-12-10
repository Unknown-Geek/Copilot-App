from flask import Flask, session
from flask_jwt_extended import create_access_token
import pytest
from unittest.mock import patch
from backend import app, limiter

@pytest.fixture
def client():
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key',
        'JWT_SECRET_KEY': 'test_jwt_secret',
        'RATELIMIT_ENABLED': True,
        'RATELIMIT_STORAGE_URL': "memory://",
    })
    
    # Clear rate limits before each test
    limiter.reset()
    
    return app.test_client()

def test_security_configuration(app):
    """Test security configuration is properly set"""
    from server import create_app
    
    app = create_app(testing=True)
    
    assert app.config['JWT_SECRET_KEY'] == 'test_secret'
    assert app.config['TESTING'] is True
    assert app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds() == 3600  # 1 hour
    assert app.config['PERMANENT_SESSION_LIFETIME'].total_seconds() == 86400  # 1 day
    assert app.secret_key is not None

def test_login_success(client):
    """Test successful login"""
    response = client.post('/auth/login',
        json={'username': 'test_user', 'password': 'test_password'},
        content_type='application/json'
    )
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_failure(client):
    """Test failed login attempts"""
    response = client.post('/auth/login',
        json={'username': '', 'password': ''},
        content_type='application/json'
    )
    assert response.status_code == 401

def test_protected_route(client):
    """Test protected route access"""
    with app.app_context():
        access_token = create_access_token(identity='test_user')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = client.get('/api/protected', headers=headers)
        assert response.status_code == 200

def test_protected_route_no_token(client):
    """Test protected route without token"""
    response = client.get('/api/protected')
    assert response.status_code == 401

def test_rate_limiting(client):
    """Test rate limiting"""
    responses = []
    # Make 6 requests in quick succession
    for _ in range(6):
        response = client.post('/auth/login',
            json={'username': 'test_user', 'password': 'test_password'},
            content_type='application/json'
        )
        responses.append(response.status_code)
    
    # First 5 should succeed, 6th should be rate limited
    assert responses[:5] == [200] * 5
    assert responses[5] == 429

def test_logout(client):
    """Test logout functionality"""
    # First login
    login_response = client.post('/auth/login',
        json={'username': 'test_user', 'password': 'test_password'},
        content_type='application/json'
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.data}"
    access_token = login_response.json['access_token']
    
    # Then logout
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/auth/logout', headers=headers)
    assert response.status_code == 200
    
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

@patch('services.github_service.GitHubService.get_access_token')
@patch('services.github_service.GitHubService.exchange_code_for_token')
def test_github_auth_flow(mock_exchange_code_for_token, mock_get_access_token, client):
    """Test GitHub OAuth flow"""
    # Mock the token exchange and access token methods
    mock_exchange_code_for_token.return_value = {'access_token': 'mock_access_token'}
    mock_get_access_token.return_value = 'mock_access_token'
    
    # Set up session state
    with client.session_transaction() as sess:
        sess['github_state'] = 'test_state'
    
    # Test callback with valid code and state
    response = client.get('/auth/github/callback?code=test_code&state=test_state')
    assert response.status_code == 200
    assert response.json == {"status": "success"}
    
    # Verify mocks were called correctly
    mock_exchange_code_for_token.assert_called_once_with('test_code')
    mock_get_access_token.assert_called_once_with('mock_access_token')