"""Attacker engine — produces the next attacker message.

Wraps the Anthropic call. Always passes the result through `safety_filter`
before returning. Never persists anything itself.
"""

from __future__ import annotations

from app.clients.anthropic_client import complete
from app.prompts.atacante_engine import build_attacker_system_prompt
from app.services.safety_filter import FilterResult, filter_attacker_message
from app.models.session import SessionState, TurnRole


def _build_messages(state: SessionState) -> list[dict[str, str]]:
    """Map our internal transcript to the Anthropic messages format.

    Defender turns become role='user'; attacker turns become role='assistant'.
    System turns (control invocations, narrator events) are folded into the
    next user message as bracketed context.
    """
    messages: list[dict[str, str]] = []
    pending_system: list[str] = []
    for m in state.transcript:
        if m.role == TurnRole.SYSTEM:
            pending_system.append(f"[evento del sistema: {m.content}]")
            continue
        if m.role == TurnRole.DEFENDER:
            content = m.content
            if pending_system:
                content = "\n".join(pending_system) + "\n" + content
                pending_system = []
            messages.append({"role": "user", "content": content})
        elif m.role == TurnRole.ATTACKER:
            messages.append({"role": "assistant", "content": m.content})
    return messages


async def generate_attacker_opening(state: SessionState) -> FilterResult:
    """First attacker turn. No prior conversation."""
    system = build_attacker_system_prompt(
        instance=state.attacker, defender=state.defender, defense=None
    )
    raw = await complete(
        system=system,
        messages=[{"role": "user", "content": "Inicia la conversación con tu apertura."}],
        max_tokens=400,
        temperature=0.85,
    )
    return filter_attacker_message(raw.strip())


async def generate_attacker_reply(
    state: SessionState, defense
) -> FilterResult:
    """Subsequent attacker turn, fed the live defense model."""
    system = build_attacker_system_prompt(
        instance=state.attacker, defender=state.defender, defense=defense
    )
    messages = _build_messages(state)
    if not messages:
        messages = [{"role": "user", "content": "Inicia la conversación."}]
    raw = await complete(
        system=system,
        messages=messages,
        max_tokens=400,
        temperature=0.8,
    )
    return filter_attacker_message(raw.strip())
