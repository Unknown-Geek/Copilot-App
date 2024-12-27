import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock
from datetime import timedelta
from dotenv import load_dotenv

# Get absolute path to backend directory
BACKEND_DIR = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, BACKEND_DIR)

# Mock azure translation module
sys.modules['azure.ai.translation.text'] = Mock()

@pytest.fixture(scope='session', autouse=True)
def load_env():
    """Load environment variables for the test session"""
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

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
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'PERMANENT_SESSION_LIFETIME': timedelta(days=1)
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers():
    return {'Authorization': 'Bearer test_token'}