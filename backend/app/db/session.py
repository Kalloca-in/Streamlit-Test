"""Async SQLAlchemy session factory.

Postgres in this app is reserved for:
- catalog snapshots (optional caching layer over the JSON sources)
- facilitator configuration
- aggregated, anonymous metrics with `n >= AGGREGATION_MIN_N`

Session content (conversations, defense models) MUST NEVER be written here.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.postgres_dsn,
        pool_pre_ping=True,
        future=True,
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_db() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as session:
        yield session


async def dispose_engine() -> None:
    engine = get_engine()
    await engine.dispose()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
