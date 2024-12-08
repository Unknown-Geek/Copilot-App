from flask import Flask
from flask_cors import CORS
from .routes import *

app = Flask(__name__)
CORS(app)

# Import routes after app initialization to avoid circular imports

__version__ = "1.0.0"