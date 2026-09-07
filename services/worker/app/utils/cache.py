import redis
import json
import hashlib
from functools import wraps
from typing import Optional, Any

from app.config import settings


class Cache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        self.redis.setex(key, ttl, json.dumps(value))

    def delete(self, key: str):
        self.redis.delete(key)

    def generate_key(self, *args, **kwargs) -> str:
        data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(data.encode()).hexdigest()


cache = Cache(settings.redis_url or "redis://localhost:6379")


def cached(ttl: int = 3600, prefix: str = ""):
    """Decorator untuk cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{cache.generate_key(*args, **kwargs)}"
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator