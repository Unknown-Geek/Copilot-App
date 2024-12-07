
import requests
from config import Config

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_repository_info(self, owner: str, repo: str) -> dict:
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        return response.json()