import unittest
from unittest.mock import patch, Mock
from services.azure_service import AzureService
from config import Config

class TestAzureService(unittest.TestCase):
    def setUp(self):
        Config.AZURE_KEY = 'test_key'
        Config.AZURE_ENDPOINT = 'https://test.azure.com'
        self.azure_service = AzureService()

    @patch('services.azure_service.TextAnalyticsClient')
    def test_analyze_sentiment(self, mock_azure_client):
        # Configure mock before initializing service
        mock_instance = Mock()
        mock_instance.analyze_sentiment.return_value = [Mock(
            sentiment='positive',
            confidence_scores=Mock(positive=0.8, neutral=0.2, negative=0.0),
            sentences=[],
            is_error=False
        )]
        mock_azure_client.return_value = mock_instance
        
        # Re-initialize service with mock
        self.azure_service.initialize()
        
        result = self.azure_service.analyze_sentiment("def greet(): print('Hello!')", 'en')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['sentiment'], 'positive')

    def test_error_handling(self):
        with patch('services.azure_service.TextAnalyticsClient') as mock_client:
            # Setup mock to raise the exact error we want
            mock_instance = Mock()
            mock_instance.analyze_sentiment.side_effect = Exception("Test error")
            mock_client.return_value = mock_instance
            
            # Re-initialize service with mock
            self.azure_service.client = mock_instance
            
            result = self.azure_service.analyze_sentiment("test code", "en")
            self.assertEqual(result['status'], 'error')
            self.assertEqual(result['error'], "Test error")

if __name__ == '__main__':
    unittest.main()