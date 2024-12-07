import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_KEY = str(os.getenv('AZURE_KEY', ''))
    AZURE_ENDPOINT = str(os.getenv('AZURE_ENDPOINT', ''))
    GITHUB_TOKEN = str(os.getenv('GITHUB_TOKEN', ''))
    GITHUB_CLIENT_ID = str(os.getenv('GITHUB_CLIENT_ID', ''))
    GITHUB_CLIENT_SECRET = str(os.getenv('GITHUB_CLIENT_SECRET', ''))
    
    @staticmethod
    def validate():
        required = [
            'AZURE_KEY', 'AZURE_ENDPOINT', 'GITHUB_TOKEN',
            'GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET'
        ]
        missing = []
        for key in required:
            value = getattr(Config, key)
            if not value or value.strip() == '':
                missing.append(f"{key} (not set in .env)")
            elif value == 'your_azure_text_analytics_key_here' or \
                 value == 'https://your-resource-name.cognitiveservices.azure.com/' or \
                 value == 'your_github_token_here':
                missing.append(f"{key} (contains default placeholder value)")
        
        if missing:
            raise ValueError(
                "Configuration Error:\n" + 
                "\n".join(f"- {m}" for m in missing) +
                "\nPlease set these values in your .env file."
            )