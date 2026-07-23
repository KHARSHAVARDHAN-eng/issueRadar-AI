import time
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.redis import get_redis


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Production rate limiting middleware enforcing request thresholds with X-RateLimit headers."""

    def __init__(
        self,
        app,
        anon_limit: int = 60,
        auth_limit: int = 300,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.anon_limit = anon_limit
        self.auth_limit = auth_limit
        self.window_seconds = window_seconds
        self._memory_counter: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip health check & docs endpoints
        path = request.url.path
        if path in ["/health", "/ready", "/live", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Identify client by user token or IP
        auth_header = request.headers.get("Authorization") or request.cookies.get("access_token")
        client_identifier = (
            auth_header[:32]
            if auth_header
            else (request.client.host if request.client else "anonymous")
        )
        limit = self.auth_limit if auth_header else self.anon_limit

        current_time = time.time()
        key = f"rate_limit:{client_identifier}"

        # Rate checking using Redis or memory fallback
        remaining = limit - 1
        reset_time = int(current_time + self.window_seconds)

        try:
            redis = await get_redis()
            if redis is not None:
                current_count = await redis.incr(key)
                if current_count == 1:
                    await redis.expire(key, self.window_seconds)
                ttl = await redis.ttl(key)
                reset_time = int(current_time + (ttl if ttl > 0 else self.window_seconds))
                remaining = max(0, limit - current_count)

                if current_count > limit:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "detail": "Rate limit exceeded. Please try again later.",
                            "retry_after": ttl,
                        },
                        headers={
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(reset_time),
                            "Retry-After": str(ttl),
                        },
                    )
            else:
                raise ValueError("Redis client unavailable")
        except Exception:
            # Memory fallback calculation
            history = self._memory_counter.get(key, [])
            history = [t for t in history if current_time - t < self.window_seconds]
            if len(history) >= limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Please try again later."},
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                    },
                )
            history.append(current_time)
            self._memory_counter[key] = history
            remaining = limit - len(history)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        return response
