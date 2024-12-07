
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_KEY = os.getenv('AZURE_KEY')
    AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    @staticmethod
    def validate():
        required = ['AZURE_KEY', 'AZURE_ENDPOINT', 'GITHUB_TOKEN']
        missing = [key for key in required if not getattr(Config, key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")