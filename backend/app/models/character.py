"""Defender identity models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DefenderKind(StrEnum):
    SELF = "self"  # User plays as themselves (levels 1-5)
    UNIVERSAL_CHARACTER = "universal_character"  # From shared catalog (6-10, 12)
    CORPORATE_CHARACTER = "corporate_character"  # From facilitator catalog (6-10, 12)


class CharacterCard(BaseModel):
    """Fictional character card. Never references real OSINT or real people."""

    code: str
    display_name: str
    age: int | None = None
    role_title: str
    fictional_company: str | None = None
    fictional_family_context: str | None = None
    exposure_profile: str
    archetype_marco: str | None = Field(
        default=None,
        description="HackTheMinds triple-rol archetype label.",
    )
    hierarchy_level: str | None = None


class DefenderIdentity(BaseModel):
    kind: DefenderKind
    character: CharacterCard | None = None

    def model_post_init(self, __context) -> None:
        if self.kind != DefenderKind.SELF and self.character is None:
            raise ValueError("character must be provided when kind != SELF")
