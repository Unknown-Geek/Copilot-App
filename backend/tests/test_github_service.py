# tests/test_github_service.py

import os
import tempfile
from services.github_service import GitHubService

def test_scan_repository():
    github_service = GitHubService()
    
    with tempfile.TemporaryDirectory() as repo_path:
        # Create some test files
        open(os.path.join(repo_path, 'test.py'), 'w').close()
        open(os.path.join(repo_path, 'test.js'), 'w').close()
        open(os.path.join(repo_path, 'README.md'), 'w').close()
        
        files = github_service.scan_repository(repo_path)
        
        assert len(files) == 2
        assert os.path.join(repo_path, 'test.py') in files
        assert os.path.join(repo_path, 'test.js') in files