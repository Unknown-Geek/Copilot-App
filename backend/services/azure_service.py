import logging
import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from config import Config

class AzureService:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
        self.azure_key = os.getenv('AZURE_KEY')
        self.azure_endpoint = os.getenv('AZURE_ENDPOINT')
        self.client = None
        self.initialize()

    def initialize(self):
        if not self.azure_key or not self.azure_endpoint:
            raise ValueError("Azure credentials not properly configured")
        
        self.client = TextAnalyticsClient(
            endpoint=self.azure_endpoint,
            credential=AzureKeyCredential(self.azure_key.strip())
        )

    def analyze_sentiment(self, code: str, language: str) -> dict:
        try:
            logging.info(f"Analyzing code for language: {language}")
            documents = [{"id": "1", "text": code, "language": language}]
            response = self.client.analyze_sentiment(documents=documents)
            return self._process_analysis(response)
        except Exception as e:
            logging.error(f"Code analysis failed: {str(e)}")
            return {"error": str(e), "status": "error"}

    def _process_analysis(self, response):
        try:
            results = []
            for doc in response:
                if doc.is_error:
                    return {"status": "error", "error": f"Document analysis failed: {doc.error}"}
                
                analysis = {
                    "status": "success",
                    "sentiment": doc.sentiment,
                    "confidence_scores": {
                        "positive": doc.confidence_scores.positive,
                        "neutral": doc.confidence_scores.neutral,
                        "negative": doc.confidence_scores.negative
                    },
                    "sentences": [{
                        "text": sent.text,
                        "sentiment": sent.sentiment,
                        "confidence_scores": {
                            "positive": sent.confidence_scores.positive,
                            "neutral": sent.confidence_scores.neutral,
                            "negative": sent.confidence_scores.negative
                        }
                    } for sent in doc.sentences]
                }
                results.append(analysis)
            
            return results[0] if results else {"status": "error", "error": "No analysis results"}
        except Exception as e:
            return {"status": "error", "error": f"Failed to process analysis: {str(e)}"}