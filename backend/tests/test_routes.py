import json
import os
import tempfile
from backend.server import create_app

def setup_test_app():
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    app.config.update({
        'TESTING': True,
        'AZURE_KEY': 'test_key',
        'AZURE_ENDPOINT': 'https://test.azure.com',
        'GITHUB_TOKEN': 'test_token',
    })
    return app

def test_scan_repository_route():
    app = setup_test_app()
    with app.test_client() as client:   
        response = client.post('/api/scan', json={'repo_path': '/path/to/repo'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'files' in data

def test_save_documentation_route():
    app = setup_test_app()
    with app.test_client() as client:   
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'output.txt')
            response = client.post('/api/save', json={
                'code': 'print("Hello, World!")',
                'language': 'python',
                'output_path': output_path
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

def test_export_markdown_route():
    app = setup_test_app()
    with app.test_client() as client:   
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'output.md')
            response = client.post('/api/export/markdown', json={
                'code': 'print("Hello, World!")',
                'language': 'python',
                'output_path': output_path
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'