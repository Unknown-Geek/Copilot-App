from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from typing import Dict, List, Optional, Any
from config import Config
from functools import lru_cache
import time
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class RateLimitConfig:
    requests_per_second: int = 10
    max_retries: int = 3
    backoff_factor: float = 1.5

class TranslationError(Exception):
    pass

class TranslatorService:
    def __init__(self):
        self.supported_languages = {'en', 'es', 'fr', 'de', 'ja', 'zh'}
        self.client = TextAnalyticsClient(
            endpoint=Config.AZURE_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_KEY)
        )
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
        """Implement rate limiting with exponential backoff."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit.requests_per_second
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.last_request_time = time.time()

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

    @lru_cache(maxsize=1000) 
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
        if target_lang not in self.supported_languages:
            return {'error': f'Unsupported target language: {target_lang}'}

        try:
            language_detection = self.client.detect_language([text])[0]
            detected_lang = language_detection.primary_language.iso6391_name

            result = self.client.translate_document(
                documents=[{"id": "1", "text": text}],
                target_language=target_lang,
                source_language=source_lang if source_lang else detected_lang
            )[0]

            if result.is_error:
                return {'error': f'Translation failed: {result.error.message}'}

            translated_text = result.translations[0].text
            translated_text = self.apply_custom_terms(
                translated_text, 
                source_lang if source_lang else detected_lang,
                target_lang
            )

            return {
                'translated_text': translated_text,
                'detected_language': detected_lang,
                'confidence': language_detection.primary_language.confidence_score
            }
            
        except Exception as e:
            return {'error': f'Translation failed: {str(e)}'}
