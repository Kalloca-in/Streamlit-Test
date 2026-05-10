"""Intra-session evaluator. Runs after every user reply.

Output is a TurnObservation that updates the DefenseModel. If the model
returns malformed JSON we fail closed: empty observation (no false signal
to the attacker), and the turn proceeds.
"""

from __future__ import annotations

import json

from app.clients.anthropic_client import complete
from app.config import get_settings
from app.models.defense import (
    DefenseModel,
    PsychHook,
    StressSignal,
    TurnObservation,
)
from app.prompts.evaluador_intra_sesion import (
    SYSTEM_PROMPT,
    build_user_message,
)


def _coerce_observation(raw: str, turn: int) -> TurnObservation:
    text = raw.strip()
    if text.startswith("```"):
        # Strip code fence if model wrapped output anyway.
        text = text.strip("`")
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace >= 0 and last_brace > first_brace:
            text = text[first_brace : last_brace + 1]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return TurnObservation(turn=turn)

    def _hooks(values: list[str]) -> list[PsychHook]:
        out: list[PsychHook] = []
        for v in values or []:
            try:
                out.append(PsychHook(v))
            except ValueError:
                continue
        return out

    try:
        stress = StressSignal(parsed.get("stress_signal", "none"))
    except ValueError:
        stress = StressSignal.NONE

    return TurnObservation(
        turn=int(parsed.get("turn", turn)),
        hooks_resisted=_hooks(parsed.get("hooks_resisted", [])),
        hooks_accepted=_hooks(parsed.get("hooks_accepted", [])),
        stress_signal=stress,
        is_critical_moment=bool(parsed.get("is_critical_moment", False)),
        notes=str(parsed.get("notes", ""))[:140] or None,
    )


async def evaluate_turn(
    *, attacker_text: str, user_text: str, turn: int
) -> TurnObservation:
    settings = get_settings()
    raw = await complete(
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_message(
                    attacker_text=attacker_text, user_text=user_text, turn=turn
                ),
            }
        ],
        model=settings.model_fast,
        max_tokens=400,
        temperature=0.0,
    )
    return _coerce_observation(raw, turn)


async def update_defense_model(
    defense: DefenseModel, observation: TurnObservation
) -> DefenseModel:
    defense.apply(observation)
    return defense
