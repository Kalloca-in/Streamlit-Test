"""Attacker archetype models (in-memory / Pydantic only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AttackerArchetype(StrEnum):
    AMIGO_SERVICIAL = "amigo_servicial"
    AUTORIDAD_APURADA = "autoridad_apurada"
    COMPLICE = "complice"
    EXPERTO_TECNICO = "experto_tecnico"
    BONDADOSO = "bondadoso"
    INSIDER = "insider"


class AttackerObjective(StrEnum):
    EXTRACT_CREDENTIAL = "extract_credential"
    INDUCE_CLICK = "induce_click"
    EXTRACT_SENSITIVE_DATA = "extract_sensitive_data"
    INDUCE_ACTION = "induce_action"


class AttackerCard(BaseModel):
    """Public-facing card describing an archetype.

    Shown to the user in levels 6-10 / 12 (chosen) and in the debrief
    (revealed) for levels 1-5.
    """

    code: AttackerArchetype
    display_name: str
    short_description: str
    techniques: list[str] = Field(default_factory=list)
    sample_opening: str
    psychological_profile: str
    accent_color: str = "#888888"


class AttackerInstance(BaseModel):
    """Concrete attacker for a session."""

    archetype: AttackerArchetype
    objective: AttackerObjective
    level: int = Field(ge=1, le=12)
