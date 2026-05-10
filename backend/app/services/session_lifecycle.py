"""Session lifecycle helpers — creation and configuration validation."""

from __future__ import annotations

import secrets
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.data_catalogs import attacker_catalog, universal_characters
from app.models.attacker import (
    AttackerArchetype,
    AttackerInstance,
    AttackerObjective,
)
from app.models.character import (
    CharacterCard,
    DefenderIdentity,
    DefenderKind,
)
from app.models.session import SessionState, SpecialMode

# Levels at which character selection is mandatory and archetype is user-picked.
_CHARACTER_REQUIRED_LEVELS = {6, 7, 8, 9, 10, 12}
# Levels at which archetype is randomly assigned.
_ARCHETYPE_RANDOM_LEVELS = {1, 2, 3, 4, 5}


class SessionConfig(BaseModel):
    """User-provided configuration for a new sparring session."""

    level: int = Field(ge=1, le=12)
    archetype: AttackerArchetype | None = None
    defender_kind: DefenderKind = DefenderKind.SELF
    universal_character_code: str | None = None
    corporate_character_code: str | None = None
    org_slug: str | None = None
    objective: AttackerObjective | None = None

    @model_validator(mode="after")
    def _enforce_rules(self) -> "SessionConfig":
        if self.level == 11:
            # Level 11 demo: no playable defender required; archetype optional.
            return self

        if self.level in _ARCHETYPE_RANDOM_LEVELS:
            if self.defender_kind != DefenderKind.SELF:
                raise ValueError(
                    "Niveles 1-5 se juegan como uno mismo, sin personaje."
                )
            # archetype is intentionally ignored in random levels.
            return self

        if self.level in _CHARACTER_REQUIRED_LEVELS:
            if self.defender_kind == DefenderKind.SELF:
                raise ValueError(
                    f"Nivel {self.level} requiere elegir un personaje, no jugarse como uno mismo."
                )
            if self.archetype is None:
                raise ValueError(
                    f"Nivel {self.level} requiere elegir explícitamente el arquetipo del atacante."
                )
            if (
                self.defender_kind == DefenderKind.UNIVERSAL_CHARACTER
                and not self.universal_character_code
            ):
                raise ValueError("Debes seleccionar un personaje universal.")
            if (
                self.defender_kind == DefenderKind.CORPORATE_CHARACTER
                and not (self.corporate_character_code and self.org_slug)
            ):
                raise ValueError(
                    "Personaje corporativo requiere `corporate_character_code` y `org_slug`."
                )
        return self


def _resolve_archetype(cfg: SessionConfig) -> AttackerArchetype:
    if cfg.archetype is not None:
        return cfg.archetype
    # Random for levels 1-5.
    archetypes = list(attacker_catalog().keys())
    rnd = secrets.randbelow(len(archetypes))
    return archetypes[rnd]


def _resolve_objective(cfg: SessionConfig, archetype: AttackerArchetype) -> AttackerObjective:
    if cfg.objective is not None:
        return cfg.objective
    # Default per-archetype mapping for sensible openings.
    mapping = {
        AttackerArchetype.AMIGO_SERVICIAL: AttackerObjective.INDUCE_CLICK,
        AttackerArchetype.AUTORIDAD_APURADA: AttackerObjective.INDUCE_ACTION,
        AttackerArchetype.COMPLICE: AttackerObjective.EXTRACT_SENSITIVE_DATA,
        AttackerArchetype.EXPERTO_TECNICO: AttackerObjective.EXTRACT_CREDENTIAL,
        AttackerArchetype.BONDADOSO: AttackerObjective.INDUCE_ACTION,
        AttackerArchetype.INSIDER: AttackerObjective.EXTRACT_SENSITIVE_DATA,
    }
    return mapping[archetype]


def _resolve_defender(cfg: SessionConfig) -> DefenderIdentity:
    if cfg.defender_kind == DefenderKind.SELF:
        return DefenderIdentity(kind=DefenderKind.SELF)
    if cfg.defender_kind == DefenderKind.UNIVERSAL_CHARACTER:
        char = universal_characters().get(cfg.universal_character_code or "")
        if char is None:
            raise ValueError(f"Personaje universal '{cfg.universal_character_code}' no existe.")
        return DefenderIdentity(
            kind=DefenderKind.UNIVERSAL_CHARACTER, character=char
        )
    # Corporate character — resolved from DB by the caller and passed in via
    # `cfg.universal_character_code` shadow path is not used here; the router
    # is responsible for loading the corporate character.
    raise NotImplementedError("Corporate character resolution is performed by the router layer.")


def build_session_state(
    cfg: SessionConfig,
    *,
    corporate_character: CharacterCard | None = None,
) -> SessionState:
    archetype = _resolve_archetype(cfg)
    objective = _resolve_objective(cfg, archetype)

    if cfg.defender_kind == DefenderKind.CORPORATE_CHARACTER:
        if corporate_character is None:
            raise ValueError("corporate_character must be provided.")
        defender = DefenderIdentity(
            kind=DefenderKind.CORPORATE_CHARACTER, character=corporate_character
        )
    else:
        defender = _resolve_defender(cfg)

    special: Literal[SpecialMode.NONE, SpecialMode.DEMOSTRACION, SpecialMode.CAJA_NEGRA]
    if cfg.level == 11:
        special = SpecialMode.DEMOSTRACION
    elif cfg.level == 12:
        special = SpecialMode.CAJA_NEGRA
    else:
        special = SpecialMode.NONE

    return SessionState(
        session_id=secrets.token_urlsafe(12),
        level=cfg.level,
        attacker=AttackerInstance(
            archetype=archetype, objective=objective, level=cfg.level
        ),
        defender=defender,
        special_mode=special,
    )
