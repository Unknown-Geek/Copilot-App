# backend/services/__init__.py
from .sentiment_service import SentimentService
from .code_analyzer import CodeAnalyzer
from .github_service import GitHubService
from .translator import TranslatorService

# Backwards compatibility
from .sentiment_service import SentimentService as AzureService

__all__ = ['SentimentService', 'AzureService', 'CodeAnalyzer', 'GitHubService', 'TranslatorService']