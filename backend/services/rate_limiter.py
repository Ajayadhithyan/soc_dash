"""
In-memory rate limiter for API endpoints.
Uses a sliding window approach to limit requests per IP.
"""

import time
import logging
from collections import defaultdict
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("soc_backend")


class InMemoryRateLimiter:
    def __init__(self):
        self._windows: dict[str, list[float]] = defaultdict(list)

    def is_limited(self, key: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds
        self._windows[key] = [t for t in self._windows[key] if t > window_start]
        if len(self._windows[key]) >= max_requests:
            return True
        self._windows[key].append(now)
        return False


_rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else "unknown"
        if _rate_limiter.is_limited(client_ip, self.max_requests, self.window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s.",
            )
        return await call_next(request)
