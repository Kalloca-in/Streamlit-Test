"""Session creation and listing.

POST /sessions creates a new sparring session in Redis (with TTL) and
returns the session id + initial state. The actual conversation happens
over the WebSocket at /ws/sessions/{session_id}.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data_catalogs import (
    attacker_catalog,
    organizational_controls,
    universal_characters,
)
from app.deps import SessionStoreDep
from app.services.session_lifecycle import SessionConfig, build_session_state

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("")
async def create_session(cfg: SessionConfig, store: SessionStoreDep):
    state = build_session_state(cfg)
    await store.save_session(state)
    return {
        "session_id": state.session_id,
        "level": state.level,
        "special_mode": state.special_mode.value,
        "ttl_seconds": store.ttl_seconds,
        # Reveal the archetype only when the user picked it (levels 6+).
        "archetype": (
            state.attacker.archetype.value if cfg.archetype is not None else None
        ),
        "objective": state.attacker.objective.value,
        "defender": state.defender.model_dump(),
    }


@router.get("/catalogs")
async def get_catalogs():
    """Catalog endpoint for the frontend configuration screen."""
    archetypes = [c.model_dump() for c in attacker_catalog().values()]
    chars = [c.model_dump() for c in universal_characters().values()]
    controls = organizational_controls()
    return {
        "archetypes": archetypes,
        "universal_characters": chars,
        "organizational_controls": controls,
    }


@router.get("/{session_id}")
async def get_session(session_id: str, store: SessionStoreDep):
    state = await store.load_session(session_id)
    if state is None:
        raise HTTPException(404, "Session not found or expired.")
    return state.model_dump()


@router.delete("/{session_id}")
async def end_session(session_id: str, store: SessionStoreDep):
    """Explicit destruction endpoint. Returns the keys that were removed."""
    keys = await store.destroy(session_id)
    return {"removed_keys": keys}
