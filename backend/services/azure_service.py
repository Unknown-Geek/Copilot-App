"""
Backwards compatibility: Import SentimentService as AzureService.
This file is deprecated - use sentiment_service.py directly.
"""

from services.sentiment_service import SentimentService, SentimentService as AzureService

__all__ = ['AzureService', 'SentimentService']