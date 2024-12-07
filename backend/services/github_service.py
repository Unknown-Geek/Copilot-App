import requests
from config import Config

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.oauth_url = "https://github.com/login/oauth"
        self.headers = {
            "Authorization": f"token {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.client_id = Config.GITHUB_CLIENT_ID
        self.client_secret = Config.GITHUB_CLIENT_SECRET

    def get_repository_info(self, owner: str, repo: str) -> dict:
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        return response.json()

    def get_oauth_url(self, redirect_uri: str, state: str = None) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': 'repo read:user',
        }
        if state:
            params['state'] = state
        return f"{self.oauth_url}/authorize"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        response = requests.post(
            f"{self.oauth_url}/access_token",
            headers={"Accept": "application/json"},
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': redirect_uri
            }
        )
        return response.json()