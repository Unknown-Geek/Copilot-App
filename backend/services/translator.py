import requests
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from typing import Dict, List, Optional, Any, Union
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
        self.client = TextTranslationClient(
            credential=AzureKeyCredential(Config.AZURE_KEY),
            endpoint=Config.AZURE_ENDPOINT
        )
        self.rate_limit = RateLimitConfig()
        self.last_request_time = 0
        self.custom_terms: Dict[str, Dict[str, str]] = {}

        self._supported_languages = None

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages for translation"""
        if not self._supported_languages:
            try:
                response = self.client.get_supported_languages()
                self._supported_languages = {
                    'translation': response.translation,
                    'transliteration': response.transliteration,
                    'dictionary': response.dictionary
                }
            except HttpResponseError as e:
                return {'error': f'Failed to get languages: {str(e)}'}
        return self._supported_languages

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
        """Translate multiple texts efficiently"""
        if not texts:
            return []

        try:
            self._rate_limit_wait()
            response = self.client.translate(
                content=texts,
                to=[target_lang],
                from_language=source_lang
            )

            results = []
            for translation in response:
                if translation.translations:
                    result = {
                        'translated_text': translation.translations[0].text,
                        'detected_language': translation.detected_language.language if translation.detected_language else source_lang,
                        'confidence': translation.detected_language.score if translation.detected_language else 1.0
                    }
                    
                    # Apply custom terminology
                    result['translated_text'] = self.apply_custom_terms(
                        result['translated_text'],
                        result['detected_language'],
                        target_lang
                    )
                    
                    results.append(result)
                else:
                    results.append({'error': 'Translation failed'})

            return results

        except HttpResponseError as e:
            return [{'error': f'Batch translation failed: {str(e)}'} for _ in texts]
        except Exception as e:
            return [{'error': f'Unexpected error: {str(e)}'} for _ in texts]

    @lru_cache(maxsize=1000) 
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
        """Translate text to target language"""
        try:
            self._rate_limit_wait()

            # Make translation request
            response = self.client.translate(
                content=[text],
                to=[target_lang],
                from_language=source_lang,
                include_sentence_length=True
            )

            if not response or not response[0].translations:
                return {'error': 'Translation failed - no result'}

            translation = response[0]
            result = {
                'translated_text': translation.translations[0].text,
                'detected_language': translation.detected_language.language if translation.detected_language else source_lang,
                'confidence': translation.detected_language.score if translation.detected_language else 1.0,
            }

            # Add sentence length metrics if available
            if translation.translations[0].sent_len:
                result['metrics'] = {
                    'source_length': translation.translations[0].sent_len.src_sent_len,
                    'target_length': translation.translations[0].sent_len.trans_sent_len
                }

            # Apply custom terminology
            result['translated_text'] = self.apply_custom_terms(
                result['translated_text'],
                result['detected_language'],
                target_lang
            )

            return result

        except HttpResponseError as e:
            return {'error': f'Translation failed: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}

    def transliterate(self, text: str, language: str, from_script: str, to_script: str) -> Dict[str, Any]:
        """Convert text between different scripts of the same language"""
        try:
            self._rate_limit_wait()
            response = self.client.transliterate(
                content=[text],
                language=language,
                from_script=from_script,
                to_script=to_script
            )
            
            if not response or not response[0]:
                return {'error': 'Transliteration failed'}

            return {
                'text': response[0].text,
                'script': response[0].script
            }

        except HttpResponseError as e:
            return {'error': f'Transliteration failed: {str(e)}'}
