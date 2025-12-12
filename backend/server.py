from flask import Flask, request
from flask_cors import CORS
from config import Config
import os
from dotenv import load_dotenv
import sys
import logging
import secrets
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

try:
    HAS_LIMITER = True
except ImportError:
    HAS_LIMITER = False

# Change relative import to absolute
from routes import api

# Initialize limiter globally
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["5 per minute"],
    strategy="fixed-window"
)

def create_app(testing=False):
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    app = Flask(__name__)
    CORS(app)
    
    # Configure security settings
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
    
    # Import and register blueprints 
    from security import security as security_bp
    app.register_blueprint(security_bp)  # Add security routes
    app.register_blueprint(api, url_prefix='/api')
    
    # Initialize JWT
    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)
    
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        if os.getenv('FLASK_ENV') == 'testing':
            app.config.update(Config.get_test_config())
        Config.validate()
        logging.info("App created successfully")
        
        # Initialize limiter with app
        limiter.init_app(app)
        
        return app
    except Exception as e:
        logging.error(f"Startup Error:\n{str(e)}")
        raise

# Create app instance at module level for gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)