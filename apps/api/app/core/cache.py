import json
import logging
from typing import Any

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class CacheService:
    """Production Redis caching service with fallback to in-memory dictionary."""

    def __init__(self):
        self._memory_cache: dict[str, Any] = {}

    async def get_json(self, key: str) -> Any | None:
        try:
            redis = await get_redis()
            if redis:
                data = await redis.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.debug(f"Redis get error for key '{key}': {e}. Checking memory fallback.")

        return self._memory_cache.get(key)

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        try:
            redis = await get_redis()
            if redis:
                serialized = json.dumps(value)
                await redis.setex(key, ttl_seconds, serialized)
            else:
                self._memory_cache[key] = value
        except Exception as e:
            logger.debug(f"Redis setex error for key '{key}': {e}. Using memory fallback.")
            self._memory_cache[key] = value

    async def delete(self, key: str) -> None:
        try:
            redis = await get_redis()
            if redis:
                await redis.delete(key)
        except Exception as e:
            logger.debug(f"Redis delete error for key '{key}': {e}.")

        self._memory_cache.pop(key, None)

    async def invalidate_pattern(self, pattern: str) -> int:
        count = 0
        try:
            redis = await get_redis()
            keys = await redis.keys(pattern)
            if keys:
                count = len(keys)
                await redis.delete(*keys)
        except Exception as e:
            logger.debug(f"Redis invalidate pattern error for '{pattern}': {e}.")

        # Invalidate in memory cache
        mem_keys = [k for k in self._memory_cache if pattern.replace("*", "") in k]
        for k in mem_keys:
            self._memory_cache.pop(k, None)
            count += 1

        return count


cache_service = CacheService()
