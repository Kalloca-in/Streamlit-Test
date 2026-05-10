"""Tests that codify session-store invariants:

- Every write sets a TTL.
- A destroyed session leaves no key behind.
- A session never persists past its TTL.
"""

from __future__ import annotations

import asyncio

import pytest

from app.models.defense import DefenseModel


pytestmark = pytest.mark.asyncio


async def test_save_session_sets_ttl(store, fake_redis, sample_session_state):
    await store.save_session(sample_session_state)
    ttl = await fake_redis.ttl(f"session:{sample_session_state.session_id}")
    assert 0 < ttl <= store.ttl_seconds


async def test_save_defense_sets_ttl(store, fake_redis):
    d = DefenseModel(session_id="sess-ttl")
    await store.save_defense(d)
    ttl = await fake_redis.ttl("session:sess-ttl:defense")
    assert 0 < ttl <= store.ttl_seconds


async def test_destroy_wipes_all_session_keys(store, fake_redis, sample_session_state):
    await store.save_session(sample_session_state)
    await store.save_defense(DefenseModel(session_id=sample_session_state.session_id))

    existed = await store.destroy(sample_session_state.session_id)
    assert len(existed) == 2

    assert await store.load_session(sample_session_state.session_id) is None
    assert await store.load_defense(sample_session_state.session_id) is None


async def test_session_expires_after_ttl(fake_redis, sample_session_state):
    """Hard TTL is enforced; the attacker forgets everything when time is up."""
    from app.services.session_store import SessionStore

    store = SessionStore(redis=fake_redis, ttl_seconds=1)
    await store.save_session(sample_session_state)
    await store.save_defense(DefenseModel(session_id=sample_session_state.session_id))

    # Advance fakeredis time past TTL.
    # fakeredis honors real time on PEXPIRE/EXPIRE; sleep 1.1s to pass.
    await asyncio.sleep(1.2)

    assert await store.load_session(sample_session_state.session_id) is None
    assert await store.load_defense(sample_session_state.session_id) is None


async def test_no_persistence_between_sessions(store, fake_redis):
    """Two separate sessions never share state."""
    from app.models.attacker import (
        AttackerArchetype,
        AttackerInstance,
        AttackerObjective,
    )
    from app.models.character import DefenderIdentity, DefenderKind
    from app.models.session import SessionState

    s1 = SessionState(
        session_id="s1",
        level=2,
        attacker=AttackerInstance(
            archetype=AttackerArchetype.BONDADOSO,
            objective=AttackerObjective.INDUCE_ACTION,
            level=2,
        ),
        defender=DefenderIdentity(kind=DefenderKind.SELF),
    )
    s2 = SessionState(
        session_id="s2",
        level=4,
        attacker=AttackerInstance(
            archetype=AttackerArchetype.EXPERTO_TECNICO,
            objective=AttackerObjective.EXTRACT_CREDENTIAL,
            level=4,
        ),
        defender=DefenderIdentity(kind=DefenderKind.SELF),
    )
    await store.save_session(s1)
    await store.save_session(s2)
    await store.destroy("s1")

    assert await store.load_session("s1") is None
    loaded = await store.load_session("s2")
    assert loaded is not None
    assert loaded.level == 4
