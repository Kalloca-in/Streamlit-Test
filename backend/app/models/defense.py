"""Intra-session defense model.

This object is the only "memory" the attacker has about the user across turns.
It lives exclusively in Redis with the session TTL. It is never serialized to
Postgres, never returned to a facilitator-facing endpoint, and never logged
with content.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class PsychHook(StrEnum):
    AUTORIDAD = "autoridad"
    URGENCIA = "urgencia"
    RECIPROCIDAD = "reciprocidad"
    PRUEBA_SOCIAL = "prueba_social"
    SIMPATIA = "simpatia"
    ESCASEZ = "escasez"
    COMPROMISO = "compromiso"
    MIEDO = "miedo"
    CURIOSIDAD = "curiosidad"
    COMPLICIDAD = "complicidad"


class StressSignal(StrEnum):
    NONE = "none"
    HESITATION = "hesitation"
    OVERSHARING = "oversharing"
    APOLOGETIC = "apologetic"
    DEFENSIVE_HARD = "defensive_hard"


class TurnObservation(BaseModel):
    turn: int
    hooks_resisted: list[PsychHook] = Field(default_factory=list)
    hooks_accepted: list[PsychHook] = Field(default_factory=list)
    stress_signal: StressSignal = StressSignal.NONE
    is_critical_moment: bool = False
    notes: str | None = None  # short, free-form, never echoed to facilitator


class DefenseModel(BaseModel):
    """Aggregated view of the user's defense posture so far in this session.

    Counts only — no transcript fragments. Used to (a) feed the attacker for
    next-turn adaptation, (b) feed the confessor at debrief time.
    """

    session_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    turns_observed: int = 0
    hook_resist_counts: dict[PsychHook, int] = Field(default_factory=dict)
    hook_accept_counts: dict[PsychHook, int] = Field(default_factory=dict)
    stress_history: list[StressSignal] = Field(default_factory=list)
    critical_moments: list[int] = Field(default_factory=list)

    def apply(self, obs: TurnObservation) -> None:
        self.turns_observed = max(self.turns_observed, obs.turn)
        for h in obs.hooks_resisted:
            self.hook_resist_counts[h] = self.hook_resist_counts.get(h, 0) + 1
        for h in obs.hooks_accepted:
            self.hook_accept_counts[h] = self.hook_accept_counts.get(h, 0) + 1
        self.stress_history.append(obs.stress_signal)
        if obs.is_critical_moment:
            self.critical_moments.append(obs.turn)
