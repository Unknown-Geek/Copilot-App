from flask import Flask
from flask_cors import CORS
from routes.api import api
from config import Config
import os
from dotenv import load_dotenv
import sys

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    print("Loading configuration...")
    if not os.path.exists('.env'):
        raise FileNotFoundError(
            ".env file not found. Please create one with AZURE_KEY, AZURE_ENDPOINT, and GITHUB_TOKEN"
        )
    
    Config.validate()
    print("Configuration validated successfully")
    app.register_blueprint(api, url_prefix='/api')
except Exception as e:
    print(f"Startup Error:\n{str(e)}", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    app.run(debug=True, port=5000)