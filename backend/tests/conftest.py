"""Shared pytest fixtures."""

from __future__ import annotations

import os

# Force test env BEFORE app imports — config validators key off this.
os.environ.setdefault("CIBERSPAR_ENV", "test")
os.environ.setdefault("SESSION_TTL_SECONDS", "60")
os.environ.setdefault("AGGREGATION_MIN_N", "10")

import fakeredis.aioredis
import pytest
import pytest_asyncio

from app.services.session_store import SessionStore


@pytest_asyncio.fixture
async def fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def store(fake_redis):
    return SessionStore(redis=fake_redis, ttl_seconds=60)


@pytest.fixture
def sample_session_state():
    from app.models.attacker import (
        AttackerArchetype,
        AttackerInstance,
        AttackerObjective,
    )
    from app.models.character import DefenderIdentity, DefenderKind
    from app.models.session import SessionState

    return SessionState(
        session_id="sess-001",
        level=3,
        attacker=AttackerInstance(
            archetype=AttackerArchetype.AUTORIDAD_APURADA,
            objective=AttackerObjective.EXTRACT_CREDENTIAL,
            level=3,
        ),
        defender=DefenderIdentity(kind=DefenderKind.SELF),
    )
