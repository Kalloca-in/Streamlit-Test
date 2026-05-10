"""Sparring WebSocket endpoint.

Wire protocol (JSON messages both ways):

Server -> client:
  { "type": "attacker_message", "content": str, "turn": int, "intercepted": bool }
  { "type": "system",            "content": str }
  { "type": "session_end",       "status": str }
  { "type": "tick",              "remaining_seconds": int }
  { "type": "error",             "content": str }

Client -> server:
  { "type": "user_message",      "content": str }
  { "type": "exit",              "reason": "dignified" }
  { "type": "invoke_control",    "control_code": str }     # level 12
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.data_catalogs import organizational_controls
from app.deps import get_session_store
from app.models.defense import DefenseModel
from app.models.session import (
    SessionState,
    SessionStatus,
    SpecialMode,
    TurnMessage,
    TurnRole,
)
from app.services.attacker_engine import (
    generate_attacker_opening,
    generate_attacker_reply,
)
from app.services.end_conditions import detect_capture, detect_victory
from app.services.evaluator import evaluate_turn, update_defense_model
from app.services.safety_filter import FilterResult

router = APIRouter(tags=["sparring"])
log = logging.getLogger("ciberspar.sparring")


async def _send_attacker(ws: WebSocket, state: SessionState, fr: FilterResult) -> None:
    msg = TurnMessage(
        role=TurnRole.ATTACKER, content=fr.safe_text, intercepted=fr.intercepted
    )
    state.append(msg)
    await ws.send_text(
        json.dumps(
            {
                "type": "attacker_message",
                "content": fr.safe_text,
                "turn": state.turn_count,
                "intercepted": fr.intercepted,
            },
            ensure_ascii=False,
        )
    )


async def _send_system(ws: WebSocket, state: SessionState, content: str) -> None:
    state.append(TurnMessage(role=TurnRole.SYSTEM, content=content))
    await ws.send_text(json.dumps({"type": "system", "content": content}, ensure_ascii=False))


async def _send_end(ws: WebSocket, status: SessionStatus) -> None:
    await ws.send_text(json.dumps({"type": "session_end", "status": status.value}))


def _resolve_control_response(control_code: str) -> str | None:
    for c in organizational_controls():
        if c["code"] == control_code:
            return (
                f"[Invocaste el control: {c['display_name']}] {c['expected_outcome']}"
            )
    return None


async def _heartbeat(ws: WebSocket, state: SessionState, ttl_seconds: int) -> None:
    """Periodic tick. Forces session close at the 30-min ceiling."""
    while True:
        await asyncio.sleep(15)
        elapsed = (datetime.now(timezone.utc) - state.started_at).total_seconds()
        remaining = max(0, ttl_seconds - int(elapsed))
        try:
            await ws.send_text(
                json.dumps({"type": "tick", "remaining_seconds": remaining})
            )
        except Exception:
            return
        if remaining <= 0:
            state.status = SessionStatus.TIMED_OUT
            return


@router.websocket("/ws/sessions/{session_id}")
async def sparring_socket(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    settings = get_settings()
    store = get_session_store()

    state = await store.load_session(session_id)
    if state is None:
        await websocket.send_text(
            json.dumps({"type": "error", "content": "Sesión inexistente o expirada."})
        )
        await websocket.close()
        return

    if state.special_mode == SpecialMode.DEMOSTRACION:
        await websocket.send_text(
            json.dumps(
                {
                    "type": "error",
                    "content": "El modo Demostración (nivel 11) usa el endpoint /demo, no este socket.",
                }
            )
        )
        await websocket.close()
        return

    defense = await store.load_defense(session_id) or DefenseModel(session_id=session_id)

    heartbeat_task = asyncio.create_task(
        _heartbeat(websocket, state, store.ttl_seconds)
    )

    try:
        # Open with the attacker's first move if the transcript is empty.
        if not state.transcript:
            opening = await generate_attacker_opening(state)
            await _send_attacker(websocket, state, opening)
            await store.save_session(state)

        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"type": "error", "content": "Mensaje JSON inválido."})
                )
                continue

            kind = payload.get("type")

            if kind == "exit":
                state.status = SessionStatus.LEFT_DIGNIFIED
                await store.save_session(state)
                await store.save_defense(defense)
                await _send_end(websocket, state.status)
                break

            if kind == "invoke_control":
                if state.special_mode != SpecialMode.CAJA_NEGRA:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "content": "Los controles solo se invocan en nivel 12 (Caja Negra).",
                            }
                        )
                    )
                    continue
                code = payload.get("control_code", "")
                response = _resolve_control_response(code)
                if response is None:
                    await websocket.send_text(
                        json.dumps(
                            {"type": "error", "content": f"Control desconocido: {code}"}
                        )
                    )
                    continue
                state.invoked_controls.append(code)
                await _send_system(websocket, state, response)
                # Invoking a control in level 12 ends the round as a victory.
                state.status = SessionStatus.VICTORY
                await store.save_session(state)
                await _send_end(websocket, state.status)
                break

            if kind != "user_message":
                continue

            user_text = (payload.get("content") or "").strip()
            if not user_text:
                continue

            state.append(TurnMessage(role=TurnRole.DEFENDER, content=user_text))
            await store.save_session(state)

            # Capture / victory detection BEFORE attacker reply.
            if detect_capture(user_text, state.attacker.objective):
                state.status = SessionStatus.CAPTURED
                await store.save_session(state)
                await store.save_defense(defense)
                await _send_end(websocket, state.status)
                break

            if detect_victory(user_text):
                state.status = SessionStatus.VICTORY
                await store.save_session(state)
                await store.save_defense(defense)
                await _send_end(websocket, state.status)
                break

            # Run evaluator + attacker in parallel.
            last_attacker = next(
                (m.content for m in reversed(state.transcript) if m.role == TurnRole.ATTACKER),
                "",
            )
            evaluator_task = asyncio.create_task(
                evaluate_turn(
                    attacker_text=last_attacker,
                    user_text=user_text,
                    turn=state.turn_count,
                )
            )
            attacker_task = asyncio.create_task(generate_attacker_reply(state, defense))

            obs = await evaluator_task
            await update_defense_model(defense, obs)
            await store.save_defense(defense)

            reply = await attacker_task
            await _send_attacker(websocket, state, reply)
            await store.save_session(state)

            # Honor heartbeat-driven timeout.
            if state.status == SessionStatus.TIMED_OUT:
                await _send_system(
                    websocket,
                    state,
                    "El atacante se cansa y desiste. Recuerda esta sensación.",
                )
                await store.save_session(state)
                await _send_end(websocket, state.status)
                break

    except WebSocketDisconnect:
        # Client closed the tab. Persist final state with TTL; nothing else.
        await store.save_session(state)
        await store.save_defense(defense)
    except Exception:
        log.exception("Unhandled error in sparring socket")
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "content": "Error interno; sesión cerrada."})
            )
        except Exception:
            pass
    finally:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except (asyncio.CancelledError, Exception):
            pass
        try:
            await websocket.close()
        except Exception:
            pass
