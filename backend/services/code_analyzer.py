"""
Code Analyzer using free sentiment analysis (TextBlob/NLTK VADER)
Replaces Azure Text Analytics - no API keys required!
"""

import logging
from services.sentiment_service import SentimentService


class CodeAnalyzer:
    """
    Analyzes code for sentiment and quality metrics using free libraries.
    No Azure credentials required!
    """
    _instance = None

    def __init__(self):
        self.sentiment_service = SentimentService()
        self.language_map = {
            'python': 'en',
            'javascript': 'en',
            'typescript': 'en',
            'java': 'en',
            'cpp': 'en',
            'csharp': 'en'
        }

    def initialize(self):
        """No initialization needed for free services."""
        pass

    def analyze_code(self, code: str, language: str) -> dict:
        """
        Analyze code for sentiment using free libraries.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Dict with sentiment analysis results
        """
        try:
            logging.info(f"Analyzing code for language: {language}")
            mapped_lang = self.language_map.get(language.lower(), 'en')
            
            # Use our free sentiment service
            result = self.sentiment_service.analyze_sentiment(code, mapped_lang)
            return result
            
        except Exception as e:
            logging.error(f"Code analysis failed: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "details": "Failed to analyze code"
            }