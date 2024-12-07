from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from config import Config
from flask import current_app

class CodeAnalyzer:
    _instance = None

    def __init__(self):
        self.client = None
        self.language_map = {
            'python': 'en',
            'javascript': 'en',
            'typescript': 'en',
            'java': 'en'
        }

    def initialize(self):
        """Lazy initialization of the Azure client"""
        if self.client is not None:
            return

        if current_app.config.get('TESTING'):
            # Use mock client for testing
            self.client = self._get_mock_client()
            return

        if not Config.AZURE_KEY or not Config.AZURE_ENDPOINT:
            raise ValueError("Azure credentials not properly configured")
        
        self.client = TextAnalyticsClient(
            endpoint=Config.AZURE_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_KEY.strip())
        )

    def _get_mock_client(self):
        """Return a mock client for testing"""
        class MockTextAnalyticsClient:
            def analyze_sentiment(self, documents):
                return [{'sentiment': 'neutral', 'confidence_scores': {'positive': 0.5, 'neutral': 0.5, 'negative': 0.0}}]
        return MockTextAnalyticsClient()

    def analyze_code(self, code: str, language: str) -> dict:
        self.initialize()  # Ensure client is initialized
        try:
            azure_lang = self.language_map.get(language.lower(), 'en')
            documents = [{"id": "1", "text": code, "language": azure_lang}]
            
            response = self.client.analyze_sentiment(
                documents=documents
            )
            return self._process_analysis(response)
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "details": "Failed to analyze code"
            }

    def _process_analysis(self, response):
        try:
            results = []
            for doc in response:
                if doc.is_error:
                    return {
                        "status": "error",
                        "error": f"Document analysis failed: {doc.error}"
                    }
                
                analysis = {
                    "status": "success",
                    "sentiment": doc.sentiment,
                    "confidence_scores": {
                        "positive": doc.confidence_scores.positive,
                        "neutral": doc.confidence_scores.neutral,
                        "negative": doc.confidence_scores.negative
                    },
                    "sentences": [{
                        "text": sent.text,
                        "sentiment": sent.sentiment,
                        "confidence_scores": {
                            "positive": sent.confidence_scores.positive,
                            "neutral": sent.confidence_scores.neutral,
                            "negative": sent.confidence_scores.negative
                        }
                    } for sent in doc.sentences]
                }
                results.append(analysis)
            
            return results[0] if results else {
                "status": "error",
                "error": "No analysis results"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to process analysis: {str(e)}"
            }