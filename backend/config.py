"""
Configuration for the DocGen backend.
Simplified - Azure credentials are no longer required!
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    # GitHub settings (optional - for GitHub integration features)
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
    
    # Security settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(32).hex())
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    @classmethod
    def get_test_config(cls) -> Dict[str, Any]:
        """Return configuration for testing environment"""
        return {
            'TESTING': True,
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_CLIENT_ID': 'test_client_id',
            'GITHUB_CLIENT_SECRET': 'test_client_secret',
            'JWT_SECRET_KEY': 'test_secret',
        }

    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """
        Validate configuration - now always succeeds since Azure is not required.
        GitHub credentials are optional.
        """
        from flask import current_app
        
        # Always use test config if FLASK_ENV is testing
        if os.getenv('FLASK_ENV') == 'testing' or (current_app and current_app.config.get('TESTING')):
            test_config = cls.get_test_config()
            if current_app:
                current_app.config.update(test_config)
            return {'status': 'valid', 'config': test_config}

        # Configuration is always valid now - no Azure required!
        config_status = {
            'github_configured': bool(cls.GITHUB_CLIENT_ID and cls.GITHUB_CLIENT_SECRET),
            'rate_limit': cls.RATE_LIMIT_PER_MINUTE
        }
        
        return {
            'status': 'valid',
            'config': config_status
        }