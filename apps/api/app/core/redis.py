import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis | None:
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=3.0,
        )
        await redis_client.ping()
        logger.info("Redis connection established successfully.")
        return redis_client
    except Exception as e:
        logger.warning(f"Failed to initialize Redis client: {e}")
        redis_client = None
        return None


async def get_redis() -> redis.Redis | None:
    global redis_client
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        logger.info("Redis client connection closed.")


async def check_redis_connection() -> bool:
    if redis_client is None:
        return False
    try:
        return bool(await redis_client.ping())
    except Exception:
        return False


async def check_redis_health() -> tuple[bool, str]:
    if redis_client is None:
        return False, "Redis client not initialized"
    try:
        ok = bool(await redis_client.ping())
        return ok, "Redis connection active" if ok else "Redis ping failed"
    except Exception as e:
        return False, f"Redis error: {e}"
