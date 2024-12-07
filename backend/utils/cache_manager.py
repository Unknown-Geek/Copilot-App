
from functools import wraps
from typing import Dict, Any, Optional
import time
import hashlib
import json

class CacheManager:
    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def _get_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        cache_data = f"{func_name}:{str(args)}:{str(kwargs)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def cache_response(self, ttl: Optional[int] = None):
        def decorator(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                cache_key = self._get_cache_key(func.__name__, args, kwargs)
                cached = self._cache.get(cache_key)
                
                if cached and time.time() < cached['expires_at']:
                    return cached['data']
                
                result = func(*args, **kwargs)
                self._cache[cache_key] = {
                    'data': result,
                    'expires_at': time.time() + (ttl or self.ttl)
                }
                return result
            return wrapped
        return decorator

    def invalidate(self, pattern: Optional[str] = None):
        if pattern:
            self._cache = {k: v for k, v in self._cache.items() if not k.startswith(pattern)}
        else:
            self._cache.clear()

cache = CacheManager()