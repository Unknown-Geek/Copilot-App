from flask import Flask
from flask_cors import CORS
from routes.api import api
from config import Config
import os
from dotenv import load_dotenv
import sys
import logging

def create_app():
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    app = Flask(__name__)
    CORS(app)
    
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Handle test configuration first
        if os.getenv('FLASK_ENV') == 'testing':
            app.config.update(Config.get_test_config())
            Config.AZURE_KEY = app.config['AZURE_KEY']
            Config.AZURE_ENDPOINT = app.config['AZURE_ENDPOINT']
            
        Config.validate()
        app.register_blueprint(api, url_prefix='/api')
        logging.info("App created successfully")
        return app
    except Exception as e:
        logging.error(f"Startup Error:\n{str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)