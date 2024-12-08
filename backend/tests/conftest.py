import pytest
import os
import sys
from pathlib import Path

# Get absolute path to backend directory
BACKEND_DIR = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, BACKEND_DIR)

@pytest.fixture
def app():
    # Only import Flask app after path is setup
    from server import create_app
    app = create_app(testing=True)
    app.config.update({
        'TESTING': True,
        'AZURE_KEY': 'test_key',
        'AZURE_ENDPOINT': 'https://test.azure.com',
        'GITHUB_TOKEN': 'test_token',
        'JWT_SECRET_KEY': 'test_secret',
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()