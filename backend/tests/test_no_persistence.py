"""Codifies the 'attacker never persists between sessions' invariant.

The attacker has no memory across sessions because:
  (a) the attacker context is rebuilt from the SessionState every turn, and
  (b) the SessionState lives only in Redis with TTL.

This test verifies the structural property: there is no place in the code
where session-specific attacker memory could leak into the next session.
"""

from __future__ import annotations

import asyncio

import pytest

from app.models.attacker import (
    AttackerArchetype,
    AttackerInstance,
    AttackerObjective,
)
from app.models.character import DefenderIdentity, DefenderKind
from app.models.defense import DefenseModel, PsychHook, TurnObservation
from app.models.session import SessionState
from app.services.session_store import SessionStore

pytestmark = pytest.mark.asyncio


async def _make_session(store: SessionStore, sid: str) -> SessionState:
    state = SessionState(
        session_id=sid,
        level=5,
        attacker=AttackerInstance(
            archetype=AttackerArchetype.AUTORIDAD_APURADA,
            objective=AttackerObjective.EXTRACT_CREDENTIAL,
            level=5,
        ),
        defender=DefenderIdentity(kind=DefenderKind.SELF),
    )
    await store.save_session(state)
    defense = DefenseModel(session_id=sid)
    defense.apply(
        TurnObservation(turn=1, hooks_accepted=[PsychHook.AUTORIDAD])
    )
    await store.save_defense(defense)
    return state


async def test_attacker_has_no_cross_session_memory(fake_redis):
    store = SessionStore(redis=fake_redis, ttl_seconds=60)

    await _make_session(store, "alpha")
    await store.destroy("alpha")

    # New session with same archetype: no carry-over.
    await _make_session(store, "beta")
    beta_def = await store.load_defense("beta")
    assert beta_def is not None
    # Beta defense has only its own observation, not alpha's.
    assert beta_def.hook_accept_counts.get(PsychHook.AUTORIDAD) == 1
    # Alpha gone entirely.
    assert await store.load_session("alpha") is None
    assert await store.load_defense("alpha") is None


async def test_concurrent_sessions_are_isolated(fake_redis):
    store = SessionStore(redis=fake_redis, ttl_seconds=60)

    await asyncio.gather(_make_session(store, "s-a"), _make_session(store, "s-b"))

    s_a_def = await store.load_defense("s-a")
    s_b_def = await store.load_defense("s-b")
    assert s_a_def is not None and s_b_def is not None
    # Mutate one, verify the other is untouched.
    s_a_def.apply(TurnObservation(turn=2, hooks_resisted=[PsychHook.URGENCIA]))
    await store.save_defense(s_a_def)

    fresh_b = await store.load_defense("s-b")
    assert fresh_b is not None
    assert fresh_b.hook_resist_counts.get(PsychHook.URGENCIA, 0) == 0
