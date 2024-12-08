from flask import Flask, request
from flask_cors import CORS
from config import Config
import os
from dotenv import load_dotenv
import sys
import logging

try:
    from flask_limiter import Limiter
    HAS_LIMITER = True
except ImportError:
    HAS_LIMITER = False

# Change relative import to absolute
from routes import api

def create_app(testing=False):
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    app = Flask(__name__)
    CORS(app)
    
    # Import and register blueprints
    app.register_blueprint(api, url_prefix='/api')  # Register with prefix
    
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        if os.getenv('FLASK_ENV') == 'testing':
            app.config.update(Config.get_test_config())
        Config.validate()
        logging.info("App created successfully")
        
        # Only setup rate limiter if not testing and package is available
        if not testing and HAS_LIMITER:
            limiter = Limiter(
                app=app,
                key_func=lambda: request.remote_addr,
                default_limits=["200 per day", "50 per hour"]
            )
        
        return app
    except Exception as e:
        logging.error(f"Startup Error:\n{str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)