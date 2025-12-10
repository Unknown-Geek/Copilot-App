"""
Translation Service using free alternatives (deep-translator + langdetect)
Replaces Azure Translator - no API keys required!
"""

import logging
from typing import Dict, List, Optional, Any
from functools import lru_cache
import time
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Free translation libraries
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logging.warning("deep-translator not available. Install with: pip install deep-translator")

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not available. Install with: pip install langdetect")


@dataclass
class RateLimitConfig:
    requests_per_second: int = 10
    max_retries: int = 3
    backoff_factor: float = 1.5


class TranslationError(Exception):
    pass


class TranslatorService:
    """
    Free translation service using Google Translate via deep-translator.
    No API keys required!
    """
    
    # Supported languages (Google Translate supports many more)
    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'es': 'spanish', 
        'fr': 'french',
        'de': 'german',
        'it': 'italian',
        'pt': 'portuguese',
        'zh-CN': 'chinese (simplified)',
        'zh': 'chinese (simplified)',
        'ja': 'japanese',
        'ko': 'korean',
        'ar': 'arabic',
        'hi': 'hindi',
        'ru': 'russian',
        'nl': 'dutch',
        'pl': 'polish',
        'tr': 'turkish',
        'vi': 'vietnamese',
        'th': 'thai',
        'id': 'indonesian',
        'sv': 'swedish'
    }
    
    def __init__(self):
        self.supported_languages = set(self.SUPPORTED_LANGUAGES.keys())
        self.rate_limit = RateLimitConfig()
        self.last_request_time = 0
        self.custom_terms: Dict[str, Dict[str, str]] = {}
    
    def add_custom_terminology(self, source_lang: str, target_lang: str, terms: Dict[str, str]) -> None:
        """Add custom terminology for specific language pair."""
        key = f"{source_lang}-{target_lang}"
        if key not in self.custom_terms:
            self.custom_terms[key] = {}
        self.custom_terms[key].update(terms)
    
    def apply_custom_terms(self, text: str, source_lang: str, target_lang: str) -> str:
        """Apply custom terminology to translated text."""
        key = f"{source_lang}-{target_lang}"
        if key in self.custom_terms:
            for source, target in self.custom_terms[key].items():
                text = text.replace(source, target)
        return text
    
    def _rate_limit_wait(self) -> None:
        """Implement rate limiting."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit.requests_per_second
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.last_request_time = time.time()
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the given text."""
        if not LANGDETECT_AVAILABLE:
            return {'language': 'en', 'confidence': 0.5}
        
        try:
            detected = detect(text)
            # Get confidence scores
            lang_probs = detect_langs(text)
            confidence = lang_probs[0].prob if lang_probs else 0.5
            
            return {
                'language': detected,
                'confidence': confidence
            }
        except Exception as e:
            logging.warning(f"Language detection failed: {e}")
            return {'language': 'en', 'confidence': 0.5}
    
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text to target language using Google Translate.
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'es', 'fr', 'de')
            source_lang: Source language code (optional, auto-detected if not provided)
            
        Returns:
            Dict with translated text and metadata
        """
        if not TRANSLATOR_AVAILABLE:
            return {'error': 'Translation library not available. Install with: pip install deep-translator'}
        
        # Normalize language code
        target_lang = target_lang.lower()
        if target_lang not in self.supported_languages:
            # Try to find a match
            if target_lang == 'chinese':
                target_lang = 'zh-CN'
            else:
                return {'error': f'Unsupported target language: {target_lang}'}
        
        try:
            self._rate_limit_wait()
            
            # Detect source language if not provided
            if not source_lang and LANGDETECT_AVAILABLE:
                detection = self.detect_language(text)
                detected_lang = detection['language']
                confidence = detection['confidence']
            else:
                detected_lang = source_lang or 'auto'
                confidence = 1.0 if source_lang else 0.5
            
            # Translate using Google Translate (free, no API key)
            translator = GoogleTranslator(source='auto', target=target_lang)
            translated_text = translator.translate(text)
            
            # Apply custom terminology
            translated_text = self.apply_custom_terms(
                translated_text,
                detected_lang,
                target_lang
            )
            
            return {
                'translated_text': translated_text,
                'detected_language': detected_lang,
                'confidence': confidence,
                'target_language': target_lang
            }
            
        except Exception as e:
            logging.error(f"Translation failed: {str(e)}")
            return {'error': f'Translation failed: {str(e)}'}
    
    def batch_translate(self, texts: List[str], target_lang: str, source_lang: Optional[str] = None) -> List[Dict[str, Any]]:
        """Translate multiple texts in parallel with rate limiting."""
        if not texts:
            return []
        
        def translate_single(text: str) -> Dict[str, Any]:
            for attempt in range(self.rate_limit.max_retries):
                try:
                    self._rate_limit_wait()
                    result = self.translate(text, target_lang, source_lang)
                    if 'error' not in result:
                        return result
                    time.sleep(self.rate_limit.backoff_factor ** attempt)
                except Exception as e:
                    if attempt == self.rate_limit.max_retries - 1:
                        return {'error': str(e)}
                    time.sleep(self.rate_limit.backoff_factor ** attempt)
            return {'error': 'Max retries exceeded'}
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(translate_single, text): i for i, text in enumerate(texts)}
            for future in as_completed(futures):
                results.append((futures[future], future.result()))
        
        # Restore original order
        return [result for _, result in sorted(results, key=lambda x: x[0])]
