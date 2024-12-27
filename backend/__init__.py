from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import os
import secrets
from dotenv import load_dotenv
from .security import security, limiter

def create_app(testing=False):
    """Create and configure the Flask application"""
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    if testing:
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['JWT_SECRET_KEY'] = 'test_jwt_secret'
        app.config['RATELIMIT_ENABLED'] = False  # Disable rate limiting in tests
    
    # Initialize extensions
    jwt = JWTManager(app)
    limiter.init_app(app)
    
    # Register blueprints
    app.register_blueprint(security)
    
    return app

app = create_app()
__version__ = "1.0.0"