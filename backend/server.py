from flask import Flask
from flask_cors import CORS
from api import create_app
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.functions import FunctionApp
from middleware import auth_middleware

app = create_app()
CORS(app)

# Initialize Azure services
credential = DefaultAzureCredential()
blob_service = BlobServiceClient(
    account_url="<your-storage-account-url>",
    credential=credential
)

# Add authentication middleware
app.before_request(auth_middleware)

if __name__ == '__main__':
    app.run(debug=True)