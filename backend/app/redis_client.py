import json
import logging
from typing import Optional

from redis import asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def init_redis():
    global redis_client
    try:
        redis_client = redis.from_url(
            url=settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
        )
        await redis_client.ping()  # type: ignore
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error("Failed to connect to Redis: ", e)
        redis_client = None


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def set_cache(key: str, value, expire: int = 3600):
    if redis_client:
        try:
            await redis_client.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.warning(f"Error setting cache for key {key}: {e}")


async def get_cache(key: str):
    if redis_client:
        try:
            data = await redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Error getting cache for key {key}: {e}")
    return None


async def delete_cache(key: str):
    if redis_client:
        try:
            await redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Error deleting cache for key {key}: {e}")


async def invalidate_prefix(prefix: str):
    if redis_client:
        try:
            keys = await redis_client.keys(f"{prefix}*")
            if keys:
                await redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} keys with prefix: {prefix}")
        except Exception as e:
            logger.warning(f"Error invalidating prefix {prefix}: {e}")
