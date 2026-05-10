"""Debrief endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.deps import SessionStoreDep
from app.models.defense import DefenseModel
from app.models.session import SessionStatus
from app.services.debrief_service import build_debrief
from app.services.metrics import record_session_outcome

router = APIRouter(prefix="/debrief", tags=["debrief"])


@router.get("/{session_id}")
async def get_debrief(session_id: str, store: SessionStoreDep, org_slug: str | None = None):
    state = await store.load_session(session_id)
    if state is None:
        raise HTTPException(404, "Sesión inexistente o expirada.")
    if state.status == SessionStatus.ACTIVE:
        raise HTTPException(409, "La sesión sigue activa; cierra primero.")

    defense = await store.load_defense(session_id) or DefenseModel(session_id=session_id)
    bundle = await build_debrief(state, defense)

    # Aggregated, anonymous outcome — bucketed write only.
    try:
        await record_session_outcome(state, org_slug=org_slug)
    except Exception:
        # Metrics are best-effort and must never block the user-facing debrief.
        pass

    return bundle.model_dump()


@router.post("/{session_id}/wipe")
async def wipe(session_id: str, store: SessionStoreDep):
    """The 'Verify deletion' button. Wipes everything and returns proof."""
    keys = await store.destroy(session_id)
    return {"removed_keys": keys, "ok": True}
