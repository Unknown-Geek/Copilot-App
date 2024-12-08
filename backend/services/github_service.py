import requests
from config import Config
from functools import lru_cache
from typing import Dict, Any, Optional, NamedTuple
from datetime import datetime, timedelta
import time
import os
from typing import List

class CachedResponse(NamedTuple):
    data: Dict[str, Any]
    expires_at: float

class GitHubService:
    def __init__(self, validate_on_init: bool = False, cache_ttl: int = 3600):
        self.base_url = "https://api.github.com"
        self.oauth_url = "https://github.com/login/oauth"
        self.default_redirect = "http://127.0.0.1:3000/auth/callback"
        
        # Initialize without validation
        self.token = Config.GITHUB_TOKEN.strip() if Config.GITHUB_TOKEN else None
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            if self.token.startswith('ghp_'):  # Personal access token
                self.headers["Authorization"] = f"token {self.token}"
            else:  # OAuth token
                self.headers["Authorization"] = f"Bearer {self.token}"
        
        self.client_id = Config.GITHUB_CLIENT_ID
        self.client_secret = Config.GITHUB_CLIENT_SECRET
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
        
        # Optional immediate validation
        if validate_on_init:
            self._validate_credentials()

        self._cache: Dict[str, CachedResponse] = {}
        self.cache_ttl = cache_ttl

    def _validate_credentials(self) -> bool:
        """Validate GitHub credentials by making a test API call"""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 401:
                return False
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

    def _check_rate_limit(self) -> bool:
        """Check if we're within GitHub's rate limits"""
        if time.time() < self.rate_limit_reset:
            if self.rate_limit_remaining <= 0:
                return False
        return True

    def _update_rate_limit(self, response: requests.Response) -> None:
        """Update rate limit info from response headers"""
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 5000))
        self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))

    def _format_repository_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format relevant repository data"""
        return {
            "name": response.get("name"),
            "full_name": response.get("full_name"),
            "description": response.get("description"),
            "language": response.get("language"),
            "stars": response.get("stargazers_count", 0),
            "forks": response.get("forks_count", 0),
            "open_issues": response.get("open_issues_count", 0),
            "topics": response.get("topics", []),
            "license": response.get("license", {}).get("name") if response.get("license") else None,
            "created_at": response.get("created_at"),
            "updated_at": response.get("updated_at"),
            "homepage": response.get("homepage"),
            "default_branch": response.get("default_branch")
        }
    
    def scan_repository(self, repo_path: str) -> List[str]:
        """
        Scan the repository for files that need documentation.

        Args:
            repo_path (str): Path to the repository

        Returns:
            List[str]: List of file paths that need documentation
        """
        files_to_document = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cpp', '.cs')):
                    files_to_document.append(os.path.join(root, file))
        return files_to_document

    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information with caching"""
        cache_key = f"{owner}/{repo}"
        
        # Check cache first
        cached = self._cache.get(cache_key)
        if cached and time.time() < cached.expires_at:
            return cached.data

        # Make API request
        if not self.token:
            return {'error': 'GitHub token not configured'}
        if not self._validate_credentials():
            return {'error': 'Invalid GitHub credentials - please check your token'}

        if not self._check_rate_limit():
            return {'error': 'GitHub API rate limit exceeded'}

        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            self._update_rate_limit(response)
            
            if response.status_code == 401:
                return {'error': 'Invalid GitHub credentials'}
            elif response.status_code == 403:
                return {'error': 'GitHub API access forbidden'}
            elif response.status_code == 404:
                return {'error': 'Repository not found'}
            
            response.raise_for_status()
            data = self._format_repository_data(response.json())
            
            # Cache the formatted response
            self._cache[cache_key] = CachedResponse(
                data=data,
                expires_at=time.time() + self.cache_ttl
            )
            
            return data
            
        except requests.exceptions.RequestException as e:
            return {'error': f'GitHub API error: {str(e)}'}

    def get_oauth_url(self, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri or self.default_redirect,
            'scope': 'repo read:user',
        }
        if state:
            params['state'] = state
        return f"{self.oauth_url}/authorize"

    def exchange_code_for_token(self, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        if not code:
            return {'error': 'No authorization code provided'}

        try:
            response = requests.post(
                f"{self.oauth_url}/access_token",
                headers={"Accept": "application/json"},
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri or self.default_redirect
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': f'GitHub OAuth error: {str(e)}',
                'status': 'error'
            }