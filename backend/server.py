from flask import Flask
from flask_cors import CORS
from routes.api import api
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Validate configuration
Config.validate()

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)