import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    AZURE_KEY = os.getenv('AZURE_COGNITIVE_SERVICES_KEY', '')
    AZURE_ENDPOINT = os.getenv('AZURE_COGNITIVE_SERVICES_ENDPOINT', '')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
    
    # Security settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(32))
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    @classmethod
    def get_test_config(cls) -> Dict[str, Any]:
        """Return configuration for testing environment"""
        return {
            'TESTING': True,
            'AZURE_KEY': 'test_key',
            'AZURE_ENDPOINT': 'https://test.azure.com',
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_CLIENT_ID': 'test_client_id',
            'GITHUB_CLIENT_SECRET': 'test_client_secret',
            'JWT_SECRET_KEY': 'test_secret',
        }

    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration with test environment support"""
        from flask import current_app
        
        if current_app and current_app.config.get('TESTING'):
            return {'status': 'valid', 'config': cls.get_test_config()}

        required = {
            'AZURE_KEY': cls.AZURE_KEY,
            'AZURE_ENDPOINT': cls.AZURE_ENDPOINT,
            'GITHUB_CLIENT_ID': cls.GITHUB_CLIENT_ID,
            'GITHUB_CLIENT_SECRET': cls.GITHUB_CLIENT_SECRET,
        }
        
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return {
            'status': 'valid',
            'config': {k: bool(v) for k, v in required.items()}
        }