"""Debrief assembly — orchestrates confessor and coach calls and returns
the full DebriefBundle that the frontend renders in six panels."""

from __future__ import annotations

import asyncio
import json
from textwrap import dedent

from app.clients.anthropic_client import complete
from app.config import get_settings
from app.models.debrief import (
    DebriefBundle,
    DebriefSummary,
    TranscriptAnnotation,
)
from app.models.defense import DefenseModel
from app.models.session import SessionState, SessionStatus
from app.prompts.coach_debrief import (
    ANNOTATIONS_SYSTEM_PROMPT,
    MIRROR_PROMPT,
    REPLAY_INVITATION_TEMPLATES,
    SUMMARY_SYSTEM_PROMPT,
    build_annotations_user_message,
    build_summary_user_message,
)
from app.prompts.confesor import SYSTEM_PROMPT as CONFESSOR_PROMPT
from app.prompts.confesor import build_user_message as build_confessor_user_message


def _defense_summary(defense: DefenseModel) -> dict:
    return {
        "turns_observed": defense.turns_observed,
        "hooks_resisted": {h.value: n for h, n in defense.hook_resist_counts.items()},
        "hooks_accepted": {h.value: n for h, n in defense.hook_accept_counts.items()},
        "stress_history": [s.value for s in defense.stress_history],
        "critical_moments": defense.critical_moments,
    }


async def _summary_headline(state: SessionState) -> str:
    raw = await complete(
        system=SUMMARY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_summary_user_message(state)}],
        max_tokens=120,
        temperature=0.4,
    )
    return raw.strip().strip('"').strip()


async def _confession(state: SessionState, defense: DefenseModel) -> str:
    raw = await complete(
        system=CONFESSOR_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_confessor_user_message(state, _defense_summary(defense)),
            }
        ],
        max_tokens=1400,
        temperature=0.85,
    )
    return raw.strip()


async def _annotations(state: SessionState) -> list[TranscriptAnnotation]:
    raw = await complete(
        system=ANNOTATIONS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_annotations_user_message(state)}],
        max_tokens=1200,
        temperature=0.3,
    )
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        first = text.find("[")
        last = text.rfind("]")
        if first >= 0 and last > first:
            text = text[first : last + 1]
    try:
        items = json.loads(text)
    except json.JSONDecodeError:
        return []
    out: list[TranscriptAnnotation] = []
    for it in items:
        try:
            out.append(TranscriptAnnotation(**it))
        except (TypeError, ValueError):
            continue
    return out


def _deletion_manifest(session_id: str) -> list[str]:
    return [
        f"Estado de la sesión: clave Redis `session:{session_id}`",
        f"Modelo de defensa intra-sesión: clave Redis `session:{session_id}:defense`",
        "Memoria contextual del atacante: vive solo en el system-prompt de la sesión actual; se pierde con el cierre.",
        "Transcripción completa de la conversación.",
    ]


def _can_replay(status: SessionStatus) -> bool:
    return status == SessionStatus.CAPTURED


async def build_debrief(state: SessionState, defense: DefenseModel) -> DebriefBundle:
    headline_task = asyncio.create_task(_summary_headline(state))
    confession_task = asyncio.create_task(_confession(state, defense))
    annotations_task = asyncio.create_task(_annotations(state))

    headline = await headline_task
    confession = await confession_task
    annotations = await annotations_task

    summary = DebriefSummary(
        status=state.status,
        turns=state.turn_count,
        duration_seconds=state.elapsed_seconds,
        headline=headline,
    )

    return DebriefBundle(
        summary=summary,
        confession=confession,
        annotations=annotations,
        can_replay=_can_replay(state.status),
        mirror_prompt=MIRROR_PROMPT,
        deletion_manifest=_deletion_manifest(state.session_id),
    )
