from typing import Dict, Any, Optional
import requests
from functools import lru_cache
from config import Config

class TranslatorService:  # Changed from TranslationService to match import
    def __init__(self):
        self.supported_languages = {'en', 'es', 'fr', 'de', 'ja', 'zh'}
        self.base_url = "https://api.cognitive.microsofttranslator.com"
        self.headers = {
            'Ocp-Apim-Subscription-Key': Config.AZURE_KEY,
            'Content-type': 'application/json'
        }

    @lru_cache(maxsize=1000)
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
        if target_lang not in self.supported_languages:
            return {'error': f'Unsupported target language: {target_lang}'}

        try:
            params = {
                'api-version': '3.0',
                'to': target_lang
            }
            if source_lang:
                params['from'] = source_lang

            response = requests.post(
                f"{self.base_url}/translate",
                headers=self.headers,
                params=params,
                json=[{'text': text}]
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                'translated_text': result[0]['translations'][0]['text'],
                'detected_language': result[0].get('detectedLanguage', {}).get('language'),
                'confidence': result[0].get('detectedLanguage', {}).get('score', 1.0)
            }
        except Exception as e:
            return {'error': f'Translation failed: {str(e)}'}