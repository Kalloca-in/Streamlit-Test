"""Redis client wrapper.

Redis is the *only* place session data ever lives. Every key written through
the session store sets an explicit TTL (see `app.services.session_store`).
"""

from __future__ import annotations

from functools import lru_cache

import redis.asyncio as redis_async

from app.config import get_settings


@lru_cache
def get_redis() -> redis_async.Redis:
    settings = get_settings()
    return redis_async.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    client = get_redis()
    await client.aclose()
    get_redis.cache_clear()
