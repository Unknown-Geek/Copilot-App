
import requests
from config import Config

class TranslatorService:
    def __init__(self):
        self.endpoint = "https://api.cognitive.microsofttranslator.com"
        self.location = "global"
        self.path = '/translate'
        self.constructed_url = self.endpoint + self.path

    def translate_text(self, text: str, target_language: str = 'en') -> dict:
        params = {
            'api-version': '3.0',
            'to': target_language
        }
        
        headers = {
            'Ocp-Apim-Subscription-Key': Config.AZURE_KEY,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json'
        }
        
        body = [{
            'text': text
        }]

        try:
            response = requests.post(
                self.constructed_url,
                params=params,
                headers=headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}