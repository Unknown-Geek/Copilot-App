
import pytest
from server import create_app
from services.code_analyzer import CodeAnalyzer
from services.github_service import GitHubService
from services.documentation_generator import DocumentationGenerator

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_analyze_endpoint(client):
    response = client.post('/api/analyze', json={
        'code': 'def test(): pass',
        'language': 'python'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'success'

def test_documentation_generation(client):
    response = client.post('/api/analyze/documentation/generate', json={
        'code': '''
        def hello():
            """Says hello"""
            print("Hello")
        ''',
        'language': 'python'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'documentation' in data

def test_github_info(client):
    response = client.get('/api/github/microsoft/vscode')
    assert response.status_code in [200, 401]  # Either success or needs auth

def test_invalid_input(client):
    response = client.post('/api/analyze', json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()