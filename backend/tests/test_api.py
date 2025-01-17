import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, Mock

# Ensure backend is in path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from server import create_app
from services.code_analyzer import CodeAnalyzer
from services.github_service import GitHubService
from services.azure_service import AzureService
from services.documentation_generator import DocumentationGenerator

@pytest.fixture
def app():
    from server import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config.update({
        'AZURE_KEY': 'test_key',
        'AZURE_ENDPOINT': 'https://test.azure.com',
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('services.azure_service.TextAnalyticsClient')
def test_analyze_endpoint_integration(mock_azure_client, client):
    # Configure mock response
    mock_response = Mock()
    mock_response.sentiment = 'positive'
    mock_response.confidence_scores = Mock(positive=0.8, neutral=0.2, negative=0.0)
    mock_response.sentences = []
    mock_response.is_error = False

    mock_instance = Mock()
    mock_instance.analyze_sentiment.return_value = [mock_response]
    mock_azure_client.return_value = mock_instance

    # Ensure AzureService is properly initialized with mock
    with patch.object(AzureService, 'initialize', return_value=None):
        azure_service = AzureService()
        azure_service.client = mock_instance

        with patch('services.azure_service.AzureService.analyze_sentiment', return_value={
            'status': 'success',
            'sentiment': 'positive',
            'confidence_scores': {
                'positive': 0.8,
                'neutral': 0.2,
                'negative': 0.0
            }
        }):
            response = client.post('/api/analyze', json={
                'code': 'def test(): pass',
                'language': 'python'
            })

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['sentiment'] == 'positive'
            assert 'confidence_scores' in data

@patch('services.azure_service.TextAnalyticsClient')
def test_analyze_endpoint(mock_azure_client, client):
    # Configure mock response
    mock_response = Mock()
    mock_response.sentiment = 'positive'
    mock_response.confidence_scores = Mock(positive=0.8, neutral=0.2, negative=0.0)
    mock_response.sentences = []
    mock_response.is_error = False

    mock_instance = Mock()
    mock_instance.analyze_sentiment.return_value = [mock_response]
    mock_azure_client.return_value = mock_instance

    with patch.object(AzureService, 'initialize', return_value=None):
        azure_service = AzureService()
        azure_service.client = mock_instance

        with patch('services.azure_service.AzureService.analyze_sentiment', return_value={
            'status': 'success',
            'sentiment': 'positive',
            'confidence_scores': {
                'positive': 0.8,
                'neutral': 0.2,
                'negative': 0.0
            }
        }):
            response = client.post('/api/analyze', json={
                'code': 'def test(): pass',
                'language': 'python'
            })

            assert response.status_code == 200
            data = response.get_json()
            assert 'status' in data
            assert data['status'] == 'success'
            assert 'sentiment' in data
            assert 'confidence_scores' in data

@patch('services.translator.TextAnalyticsClient')
def test_translate_endpoint(mock_analytics_client, client):
    # Configure mock responses
    mock_language_detection = Mock()
    mock_language_detection.primary_language.iso6391_name = 'en'
    mock_language_detection.primary_language.confidence_score = 0.95

    mock_translation = Mock()
    mock_translation.translations = [Mock(text='Bonjour')]
    mock_translation.is_error = False

    mock_instance = Mock()
    mock_instance.detect_language.return_value = [mock_language_detection]
    mock_instance.translate_document.return_value = [mock_translation]
    mock_analytics_client.return_value = mock_instance

    # Mock the translator service initialization
    with patch('services.translator.TranslatorService.__init__', return_value=None):
        with patch('services.translator.TranslatorService.translate') as mock_translate:
            mock_translate.return_value = {
                'translated_text': 'Bonjour',
                'detected_language': 'en',
                'confidence': 0.95
            }

            try:
                response = client.post('/api/translate', json={
                    'text': 'Hello',
                    'target_language': 'fr'
                })
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                raise

            assert response.status_code == 200
            data = response.get_json()
            assert data['translated_text'] == 'Bonjour'
            assert data['detected_language'] == 'en'
            assert data['confidence'] == 0.95

@patch('services.azure_service.TextAnalyticsClient')
def test_translate_endpoint(mock_analytics_client, client):
    # Configure mock responses
    mock_language_detection = Mock()
    mock_language_detection.primary_language.iso6391_name = 'en'
    mock_language_detection.primary_language.confidence_score = 0.95
    mock_translation = Mock()
    mock_translation.translations = [Mock(text='Bonjour')]
    mock_translation.is_error = False
    mock_instance = Mock()
    mock_instance.detect_language.return_value = [mock_language_detection]
    mock_instance.translate_document.return_value = [mock_translation]
    mock_analytics_client.return_value = mock_instance

    with patch('services.translator.TranslatorService.__init__', return_value=None):
        with patch('services.translator.TranslatorService.translate') as mock_translate:
            # Success case
            mock_translate.return_value = {
                'translated_text': 'Bonjour',
                'detected_language': 'en',
                'confidence': 0.95
            }
            response = client.post('/api/translate', json={
                'text': 'Hello',
                'target_language': 'fr'
            })
            assert response.status_code == 200
            assert response.json['status'] == 'success'
            assert 'metrics' in response.json

            # Invalid input cases
            response = client.post('/api/translate', json={
                'text': None,
                'target_language': 'fr'
            })
            assert response.status_code == 400

            response = client.post('/api/translate', json={
                'text': 'Hello'
            })
            assert response.status_code == 400

            # Error case
            mock_translate.side_effect = Exception('Translation failed')
            response = client.post('/api/translate', json={
                'text': 'Hello',
                'target_language': 'fr'
            })
            assert response.status_code == 500
            assert response.json['status'] == 'error'

@patch('services.translator.TextAnalyticsClient')
def test_batch_translate_endpoint(mock_analytics_client, client):
    mock_instance = Mock()
    mock_instance.detect_language.return_value = [
        Mock(
            primary_language=Mock(
                iso6391_name='en',
                confidence_score=0.95
            )
        )
    ]
    mock_instance.translate_document.return_value = [
        Mock(translations=[Mock(text='Bonjour')], is_error=False)
    ]
    mock_analytics_client.return_value = mock_instance

    with patch('services.translator.TranslatorService.__init__', return_value=None):
        with patch('services.translator.TranslatorService.batch_translate') as mock_translate:
            mock_translate.return_value = [
                {
                    'translated_text': 'Bonjour',
                    'detected_language': 'en',
                    'confidence': 0.95
                }
            ]

            response = client.post('/api/translate/batch', json={
                'texts': ['Hello'],
                'target_language': 'fr'
            })
            
            assert response.status_code == 200
            assert 'translations' in response.json
            assert len(response.json['translations']) == 1

@patch('services.translator.TextAnalyticsClient')
def test_custom_terminology(mock_analytics_client, client):
    mock_instance = Mock()
    mock_instance.detect_language.return_value = [
        Mock(
            primary_language=Mock(
                iso6391_name='en',
                confidence_score=0.95
            )
        )
    ]
    mock_instance.translate_document.return_value = [
        Mock(translations=[Mock(text='Bonjour')], is_error=False)
    ]
    mock_analytics_client.return_value = mock_instance

    with patch('services.translator.TranslatorService.__init__', return_value=None):
        with patch('services.translator.TranslatorService.translate') as mock_translate:
            mock_translate.return_value = {
                'translated_text': 'Bonjour mon ami',
                'detected_language': 'en',
                'confidence': 0.95
            }

            # Test adding custom terminology
            response = client.post('/api/translate/terminology', json={
                'source_lang': 'en',
                'target_lang': 'fr',
                'terms': {'friend': 'ami'}
            })
            assert response.status_code == 200

            # Test translation with custom terms
            response = client.post('/api/translate', json={
                'text': 'Hello friend',
                'target_language': 'fr'
            })
            assert response.status_code == 200
            assert 'ami' in response.json['translated_text']

def test_documentation_endpoint_integration(client):
    test_code = '''"""Test function"""
def test():
    pass'''  # Note: removed indentation
    
    response = client.post('/api/analyze/documentation', json={
        'code': test_code,
        'language': 'python'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'documentation' in data

def test_documentation_generation(client):
    test_code = '''def hello():
    """Says hello"""
    print("Hello")'''  # Note: removed indentation
    
    response = client.post('/api/analyze/documentation/generate', json={
        'code': test_code,
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