"""
Sentiment Analysis Service using free alternatives (TextBlob + NLTK VADER)
Replaces Azure Text Analytics - no API keys required!
"""

import logging
from typing import Dict, Any, List

# Initialize NLTK VADER on first import
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    logging.warning("NLTK not available. Install with: pip install nltk")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available. Install with: pip install textblob")


class SentimentService:
    """
    Free sentiment analysis service using TextBlob and NLTK VADER.
    No API keys required!
    """
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        self.language_map = {
            'python': 'en',
            'javascript': 'en',
            'typescript': 'en',
            'java': 'en',
            'cpp': 'en',
            'csharp': 'en'
        }
    
    def analyze_sentiment(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Analyze sentiment of text using VADER (better for code comments)
        and TextBlob as fallback.
        
        Args:
            text: Text to analyze
            language: Language code (default: 'en')
            
        Returns:
            Dict with sentiment analysis results
        """
        try:
            logging.info(f"Analyzing sentiment for language: {language}")
            
            # Use VADER for English text (better for code/technical content)
            if VADER_AVAILABLE and language in ['en', 'python', 'javascript', 'typescript', 'java']:
                return self._analyze_with_vader(text)
            
            # Fallback to TextBlob
            if TEXTBLOB_AVAILABLE:
                return self._analyze_with_textblob(text)
            
            return {
                "status": "error",
                "error": "No sentiment analysis library available"
            }
            
        except Exception as e:
            logging.error(f"Sentiment analysis failed: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze using NLTK VADER - excellent for code comments."""
        scores = self.vader.polarity_scores(text)
        
        # Determine overall sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Analyze sentences individually
        sentences = self._split_sentences(text)
        sentence_results = []
        for sent in sentences:
            sent_scores = self.vader.polarity_scores(sent)
            sent_compound = sent_scores['compound']
            sent_sentiment = 'positive' if sent_compound >= 0.05 else ('negative' if sent_compound <= -0.05 else 'neutral')
            sentence_results.append({
                "text": sent,
                "sentiment": sent_sentiment,
                "confidence_scores": {
                    "positive": max(0, sent_scores['pos']),
                    "neutral": max(0, sent_scores['neu']),
                    "negative": max(0, sent_scores['neg'])
                }
            })
        
        return {
            "status": "success",
            "sentiment": sentiment,
            "confidence_scores": {
                "positive": max(0, scores['pos']),
                "neutral": max(0, scores['neu']),
                "negative": max(0, scores['neg'])
            },
            "compound_score": compound,
            "sentences": sentence_results
        }
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Fallback analysis using TextBlob."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Convert polarity to sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Convert polarity to confidence scores
        positive = max(0, polarity)
        negative = max(0, -polarity)
        neutral = 1 - abs(polarity)
        
        # Normalize
        total = positive + negative + neutral
        if total > 0:
            positive /= total
            negative /= total
            neutral /= total
        
        return {
            "status": "success",
            "sentiment": sentiment,
            "confidence_scores": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentences": []
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]


# Backwards compatibility alias
class AzureService(SentimentService):
    """Alias for backwards compatibility with existing code."""
    pass
