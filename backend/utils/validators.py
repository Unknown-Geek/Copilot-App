from typing import Dict, Any
from functools import lru_cache

@lru_cache(maxsize=100)
def get_supported_languages() -> set:
    return {'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp'}

def validate_code_input(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
        
    required_fields = ['code', 'language']
    if not all(field in data for field in required_fields):
        return False
        
    if not isinstance(data['code'], str) or not data['code'].strip():
        return False
        
    if not isinstance(data['language'], str) or not data['language'].strip():
        return False
        
    # Enhanced language validation
    supported_languages = get_supported_languages()
    if data['language'].lower() not in supported_languages:
        return False
        
    # Add code size limit
    if len(data['code']) > 50000:  # 50KB limit
        return False
        
    return True

def validate_github_params(owner: str, repo: str) -> bool:
    if not owner or not repo:
        return False
    if len(owner) > 100 or len(repo) > 100:
        return False
    if not all(c.isalnum() or c in '-_.' for c in owner + repo):
        return False
    return True