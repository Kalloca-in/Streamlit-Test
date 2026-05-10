"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.clients.redis_client import get_redis
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readiness() -> dict[str, object]:
    settings = get_settings()
    redis_ok = False
    try:
        redis_ok = bool(await get_redis().ping())
    except Exception:
        redis_ok = False
    return {
        "redis": redis_ok,
        "session_ttl_seconds": settings.session_ttl_seconds,
        "aggregation_min_n": settings.aggregation_min_n,
        "model": settings.model,
    }
