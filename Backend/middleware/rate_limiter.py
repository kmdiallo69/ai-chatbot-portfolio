import time
import logging
from typing import Dict, Optional
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings

logger = logging.getLogger(__name__)

@dataclass
class RateLimitEntry:
    """Entry in the rate limiter cache"""
    count: int = 0
    reset_time: float = 0
    last_attempt: float = 0

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI
    In production, use Redis or another distributed cache
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.cache: Dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self.limits = settings.RATE_LIMITS
        
        # Define endpoint patterns and their rate limit types
        self.endpoint_patterns = {
            '/auth/login': 'login',
            '/auth/register': 'register',
            '/auth/verify-email': 'verify_email',
            '/auth/reset-password': 'reset_password',
            '/chat': 'chat',
            '/chat/image': 'chat',
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "127.0.0.1"
    
    def _get_endpoint_type(self, path: str) -> str:
        """Get rate limit type for endpoint"""
        for pattern, limit_type in self.endpoint_patterns.items():
            if path.startswith(pattern):
                return limit_type
        return 'general'
    
    def _get_key(self, identifier: str, endpoint_type: str) -> str:
        """Generate cache key for rate limiting"""
        return f"{endpoint_type}:{identifier}"
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry.reset_time
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def _is_rate_limited(self, identifier: str, endpoint_type: str) -> tuple[bool, Optional[int], int]:
        """
        Check if identifier is rate limited for the endpoint
        
        Returns:
            (is_limited, seconds_until_reset, remaining_requests)
        """
        self._cleanup_expired()
        
        key = self._get_key(identifier, endpoint_type)
        current_time = time.time()
        
        if endpoint_type not in self.limits:
            endpoint_type = 'general'
        
        limit_config = self.limits[endpoint_type]
        max_requests = limit_config['requests']
        window_seconds = limit_config['window']
        
        entry = self.cache[key]
        
        # If reset time has passed, reset the counter
        if current_time > entry.reset_time:
            entry.count = 0
            entry.reset_time = current_time + window_seconds
        
        # Check if limit exceeded
        if entry.count >= max_requests:
            seconds_until_reset = int(entry.reset_time - current_time)
            return True, seconds_until_reset, 0
        
        remaining = max_requests - entry.count
        return False, None, remaining
    
    def _record_request(self, identifier: str, endpoint_type: str):
        """Record a request for rate limiting"""
        key = self._get_key(identifier, endpoint_type)
        current_time = time.time()
        
        if endpoint_type not in self.limits:
            endpoint_type = 'general'
        
        limit_config = self.limits[endpoint_type]
        window_seconds = limit_config['window']
        
        entry = self.cache[key]
        
        # If reset time has passed, reset the counter
        if current_time > entry.reset_time:
            entry.count = 0
            entry.reset_time = current_time + window_seconds
        
        entry.count += 1
        entry.last_attempt = current_time
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting"""
        try:
            # Skip rate limiting for health checks and static files
            if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
                return await call_next(request)
            
            # Get client identifier and endpoint type
            client_ip = self._get_client_ip(request)
            endpoint_type = self._get_endpoint_type(request.url.path)
            
            # Check rate limit
            is_limited, reset_time, remaining = self._is_rate_limited(client_ip, endpoint_type)
            
            if is_limited:
                logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_type}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Rate limit exceeded. Try again in {reset_time} seconds.",
                        "retry_after": reset_time
                    },
                    headers={
                        "Retry-After": str(reset_time),
                        "X-RateLimit-Limit": str(self.limits.get(endpoint_type, self.limits['general'])['requests']),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time() + (reset_time or 0)))
                    }
                )
            
            # Record the request
            self._record_request(client_ip, endpoint_type)
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit"] = str(self.limits.get(endpoint_type, self.limits['general'])['requests'])
            response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
            reset_timestamp = int(self.cache[self._get_key(client_ip, endpoint_type)].reset_time)
            response.headers["X-RateLimit-Reset"] = str(reset_timestamp)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {str(e)}")
            # If rate limiting fails, continue with the request
            return await call_next(request)

# Utility functions for manual rate limiting checks
class RateLimiter:
    """Utility class for manual rate limiting checks in services"""
    
    def __init__(self, middleware: RateLimitMiddleware):
        self.middleware = middleware
    
    def is_rate_limited(self, identifier: str, endpoint_type: str = 'general') -> tuple[bool, Optional[int]]:
        """Check if identifier is rate limited"""
        is_limited, reset_time, _ = self.middleware._is_rate_limited(identifier, endpoint_type)
        return is_limited, reset_time
    
    def record_request(self, identifier: str, endpoint_type: str = 'general'):
        """Record a request"""
        self.middleware._record_request(identifier, endpoint_type)
    
    def clear_limit(self, identifier: str, endpoint_type: str = 'general'):
        """Clear rate limit for identifier"""
        key = self.middleware._get_key(identifier, endpoint_type)
        if key in self.middleware.cache:
            del self.middleware.cache[key] 