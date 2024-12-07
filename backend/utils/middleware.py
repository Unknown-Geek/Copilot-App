from functools import wraps
from flask import request, jsonify, current_app
import time
from typing import Dict, Callable
from threading import Lock

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        self.lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self.lock:
            if key not in self.requests:
                self.requests[key] = []
            
            # Remove old requests
            self.requests[key] = [t for t in self.requests[key] if now - t < 60]
            
            if len(self.requests[key]) >= self.requests_per_minute:
                return False
                
            self.requests[key].append(now)
            return True

def rate_limit(limiter: RateLimiter):
    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = f"{request.remote_addr}:{f.__name__}"
            if not limiter.is_allowed(key):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': '60 seconds'
                }), 429
            return f(*args, **kwargs)
        return wrapped
    return decorator

def require_auth(f: Callable):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
            
        # Allow test token in testing environment
        if current_app.config.get('TESTING'):  # Changed from request.app to current_app
            if auth_header == 'Bearer test_token':
                return f(*args, **kwargs)
                
        # Normal auth validation
        try:
            token_type, token = auth_header.split(' ')
            if not token or token_type.lower() not in ('bearer', 'token'):
                return jsonify({'error': 'Invalid authorization format'}), 401
        except ValueError:
            return jsonify({'error': 'Invalid authorization format'}), 401
            
        return f(*args, **kwargs)
    return wrapped