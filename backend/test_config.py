import unittest
from unittest.mock import patch, Mock
from flask import current_app
from server import create_app
from services.code_analyzer import CodeAnalyzer
from services.documentation_generator import DocumentationGenerator
from models.documentation import Documentation, CodeBlock
from config import Config

class TestAPIFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'AZURE_KEY': 'test_key',
            'AZURE_ENDPOINT': 'https://test.azure.com',
            'GITHUB_TOKEN': 'test_token',
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('services.code_analyzer.TextAnalyticsClient')
    def test_azure_integration(self, mock_azure_client):
        """Test Azure Text Analytics integration"""
        test_code = "def greet(): print('Hello!')"

        # Configure mock response
        mock_response = Mock()
        mock_response.sentiment = 'positive'
        mock_response.confidence_scores = Mock(
            positive=0.8,
            neutral=0.2,
            negative=0.0
        )
        mock_response.sentences = []
        mock_response.is_error = False
        
        # Set up mock client behavior
        mock_azure_client.return_value.analyze_sentiment.return_value = [mock_response]
        
        # Make request
        response = self.client.post('/api/analyze', json={
            'code': test_code,
            'language': 'python'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['analysis']['sentiment'], 'positive')

    def test_code_analysis_with_comments(self):
        """Test code analysis with different comment styles"""
        with patch('services.code_analyzer.CodeAnalyzer.analyze_code') as mock_analyze:
            mock_analyze.return_value = {
                'status': 'success',
                'sentiment': 'neutral',
                'confidence_scores': {'positive': 0.3, 'neutral': 0.6, 'negative': 0.1},
                'sentences': []
            }
            
            test_data = {
                'code': '''
                # Single line comment
                """
                Multi-line docstring
                with additional info
                """
                def test():
                    # Function comment
                    return True
                ''',
                'language': 'python'
            }
            response = self.client.post('/api/analyze', json=test_data)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['status'], 'success')

    def test_documentation_with_multiple_languages(self):
        """Test documentation generation for different languages"""
        with patch('services.documentation_generator.DocumentationGenerator.generate') as mock_generate:
            mock_generate.return_value = {
                'title': 'Test Documentation',
                'description': 'Test description',
                'code_blocks': [],
                'generated_at': '2024-01-01T00:00:00',
                'language': 'python'
            }
            
            test_data = {
                'code': 'def test(): pass',
                'language': 'python'
            }
            response = self.client.post('/api/analyze/documentation', json=test_data)
            self.assertEqual(response.status_code, 200)

    def test_input_validation_strict(self):
        """Test strict input validation rules"""
        test_cases = [
            {'code': '', 'language': 'python'},  # Empty code
            {'code': 'def test():', 'language': ''},  # Empty language
            {'code': 'def test():', 'language': 'invalid'},  # Invalid language
            {'code': None, 'language': 'python'},  # None code
            {}  # Empty payload
        ]
        
        for test_case in test_cases:
            response = self.client.post('/api/analyze', json=test_case)
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn('error', data)

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test invalid JSON
        response = self.client.post('/api/analyze', data='invalid json')
        self.assertEqual(response.status_code, 400)

        # Test missing content type
        response = self.client.post('/api/analyze', data={})
        self.assertEqual(response.status_code, 400)

        # Test invalid endpoint
        response = self.client.get('/api/invalid')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()