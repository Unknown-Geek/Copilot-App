import requests
from config import Config
from functools import lru_cache
from typing import Dict, Any, Optional, NamedTuple
from datetime import datetime, timedelta
import time
import os
from typing import List
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import secrets
from urllib.parse import urlencode  # Add this import
from flask import jsonify  # Add this import

@dataclass
class CachedResponse:
    data: Any
    expires_at: float

class GitHubService:
    def __init__(self, validate_on_init: bool = False, cache_ttl: int = 3600):
        self.base_url = "https://api.github.com"
        self.oauth_url = "https://github.com/login/oauth"
        self.default_redirect = "https://codedoc-vscode-extension.onrender.com/auth/callback"
        
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
        """Get repository information with improved caching"""
        cache_key = f"{owner}/{repo}"
        
        # Check cache first with stale-while-revalidate strategy
        cached = self._cache.get(cache_key)
        current_time = time.time()
        
        # Return cached response if still fresh
        if cached and current_time < cached.expires_at:
            return cached.data
            
        # Start background refresh if stale but not expired
        if cached and current_time < (cached.expires_at + 300):  # 5 min grace period
            self._refresh_cache_async(owner, repo, cache_key)
            return cached.data

        return self._fetch_repository_info(owner, repo, cache_key)

    def _refresh_cache_async(self, owner: str, repo: str, cache_key: str) -> None:
        """Refresh cache asynchronously"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self._fetch_repository_info, owner, repo, cache_key)

    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Advanced repository analysis"""
        try:
            # Get basic repo info
            repo_info = self.get_repository_info(owner, repo)
            if 'error' in repo_info:
                return repo_info

            # Get additional data in parallel
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    'contributors': executor.submit(self._get_contributors, owner, repo),
                    'languages': executor.submit(self._get_languages, owner, repo),
                    'activity': executor.submit(self._get_activity_metrics, owner, repo)
                }
                
                results = {}
                for key, future in futures.items():
                    try:
                        results[key] = future.result()
                    except Exception as e:
                        results[key] = {'error': str(e)}

            # Combine all data
            analysis = {
                'basic_info': repo_info,
                'contributors': results['contributors'],
                'languages': results['languages'],
                'activity': results['activity'],
                'analyzed_at': time.time()
            }

            # Cache the analysis
            cache_key = f"{owner}/{repo}/analysis"
            self._cache[cache_key] = CachedResponse(
                data=analysis,
                expires_at=time.time() + self.cache_ttl
            )

            return analysis

        except Exception as e:
            logging.error(f"Repository analysis failed: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}

    def batch_process_repositories(self, repos: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process multiple repositories in parallel"""
        results = {}
        errors = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_repo = {
                executor.submit(self.analyze_repository, repo['owner'], repo['name']): repo
                for repo in repos
            }
            
            for future in as_completed(future_to_repo):
                repo = future_to_repo[future]
                repo_key = f"{repo['owner']}/{repo['name']}"
                try:
                    results[repo_key] = future.result()
                except Exception as e:
                    errors.append({
                        'repo': repo_key,
                        'error': str(e)
                    })

        return {
            'results': results,
            'errors': errors,
            'total': len(repos),
            'successful': len(results),
            'failed': len(errors)
        }

    def _get_contributors(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository contributors with statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            contributors = response.json()
            return {
                'total_contributors': len(contributors),
                'top_contributors': contributors[:10]
            }
        return {'error': f'Failed to fetch contributors: {response.status_code}'}

    def _get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository language statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            languages = response.json()
            total = sum(languages.values())
            return {
                'languages': languages,
                'percentages': {lang: (count/total)*100 for lang, count in languages.items()}
            }
        return {'error': f'Failed to fetch languages: {response.status_code}'}

    def _get_activity_metrics(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository activity metrics"""
        # Get commit activity
        commit_url = f"{self.base_url}/repos/{owner}/{repo}/stats/commit_activity"
        commit_response = requests.get(commit_url, headers=self.headers)
        
        # Get code frequency
        frequency_url = f"{self.base_url}/repos/{owner}/{repo}/stats/code_frequency"
        frequency_response = requests.get(frequency_url, headers=self.headers)
        
        metrics = {
            'commit_activity': commit_response.json() if commit_response.status_code == 200 else None,
            'code_frequency': frequency_response.json() if frequency_response.status_code == 200 else None,
            'collected_at': time.time()
        }
        
        return metrics

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

    def get_authorization_url(self, state=None):
        client_id = Config.GITHUB_CLIENT_ID
        redirect_uri = self.default_redirect
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'repo user',
        }
        if state:
            params['state'] = state
        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
        return jsonify({'auth_url': auth_url})

    def get_access_token(self, code: str) -> str:
        data = {
            'client_id': Config.GITHUB_CLIENT_ID,
            'client_secret': Config.GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': self.default_redirect
        }
        response = requests.post(f"{self.oauth_url}/access_token", 
                                 headers={"Accept": "application/json"},
                                 data=data)
        if response.status_code != 200:
            raise Exception("Failed to get access token")
        return response.json()['access_token']

    def validate_token(self):
        if not self.token:
            raise ValueError("GitHub token is not set")

    def get_repository_info(self, owner, repo):
        if not self.token:
            return {'error': 'GitHub token not configured'}
        headers = {'Authorization': f'token {self.token}'}
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(repo_url, headers=headers)
        if response.status_code == 401:
            return {'error': 'Invalid GitHub credentials'}
        response.raise_for_status()
        return response.json()