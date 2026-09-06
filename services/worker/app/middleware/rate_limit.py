import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class RateLimitConfig:
    max_requests: int = 60
    window_seconds: int = 60


class RateLimiter:
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def _clean_old_requests(self, client_ip: str, now: float):
        cutoff = now - self.config.window_seconds
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > cutoff]
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        self._clean_old_requests(client_ip, now)
        
        if len(self.requests[client_ip]) >= self.config.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining(self, client_ip: str) -> int:
        now = time.time()
        self._clean_old_requests(client_ip, now)
        return max(0, self.config.max_requests - len(self.requests[client_ip]))
    
    def get_reset_time(self, client_ip: str) -> int:
        if not self.requests[client_ip]:
            return 0
        return int(self.requests[client_ip][0] + self.config.window_seconds)


rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/api/status", "/api/health"]:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        
        if not rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": rate_limiter.config.max_requests,
                    "window_seconds": rate_limiter.config.window_seconds,
                    "retry_after": rate_limiter.get_reset_time(client_ip) - int(time.time()),
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.config.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_ip))
        response.headers["X-RateLimit-Reset"] = str(rate_limiter.get_reset_time(client_ip))
        
        return response