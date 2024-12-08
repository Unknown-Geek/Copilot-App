import pytest
import sys
import os
from pathlib import Path

# Add the backend directory to the PYTHONPATH
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
    
# Change the import to use the absolute path
from server import create_app

# Mock rate limiter for testing
class MockLimiter:
    def limit(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

@pytest.fixture
def app():
    app = create_app(testing=True)  # Pass testing flag
    app.config.update({
        'TESTING': True,
        'AZURE_KEY': 'test_key',
        'AZURE_ENDPOINT': 'https://test.azure.com',
        'GITHUB_TOKEN': 'test_token',
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()