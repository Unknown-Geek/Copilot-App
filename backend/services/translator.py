from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from typing import Dict, List, Optional, Any
from config import Config
from functools import lru_cache

class TranslationError(Exception):
    pass

class TranslatorService:
    def __init__(self):
        self.supported_languages = {'en', 'es', 'fr', 'de', 'ja', 'zh'}
        self.client = TextAnalyticsClient(
            endpoint=Config.AZURE_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_KEY)
        )

    @lru_cache(maxsize=1000) 
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
        if target_lang not in self.supported_languages:
            return {'error': f'Unsupported target language: {target_lang}'}

        try:
            # Use textanalytics detect_language first
            language_detection = self.client.detect_language([text])[0]
            detected_lang = language_detection.primary_language.iso6391_name
            
            # Then use textanalytics translate
            result = self.client.translate_document(
                documents=[{"id": "1", "text": text}],
                target_language=target_lang,
                source_language=source_lang if source_lang else detected_lang
            )[0]

            if result.is_error:
                return {'error': f'Translation failed: {result.error.message}'}

            return {
                'translated_text': result.translations[0].text,
                'detected_language': detected_lang,
                'confidence': language_detection.primary_language.confidence_score
            }
            
        except Exception as e:
            return {'error': f'Translation failed: {str(e)}'}
