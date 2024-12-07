from flask import Flask
from flask_cors import CORS
from routes.api import api
from config import Config
import os
from dotenv import load_dotenv
import sys

def create_app():
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    app = Flask(__name__)
    CORS(app)
    
    try:
        Config.validate()
        app.register_blueprint(api, url_prefix='/api')
        return app
    except Exception as e:
        print(f"Startup Error:\n{str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)