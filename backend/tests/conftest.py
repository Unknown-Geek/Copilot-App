
import pytest
from server import create_app

@pytest.fixture
def app():
    app = create_app()
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