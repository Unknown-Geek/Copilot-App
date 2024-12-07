
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from config import Config

class CodeAnalyzer:
    def __init__(self):
        self.client = TextAnalyticsClient(
            endpoint=Config.AZURE_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_KEY)
        )

    def analyze_code(self, code: str, language: str) -> dict:
        try:
            response = self.client.analyze_text(
                documents=[code],
                language=language
            )
            return self._process_analysis(response)
        except Exception as e:
            return {"error": str(e)}

    def _process_analysis(self, response):
        # Process Azure analysis response
        return {"analysis": response}