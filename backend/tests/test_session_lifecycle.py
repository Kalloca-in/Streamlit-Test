"""Validate the configuration rules for the four session-construction modes."""

from __future__ import annotations

import pytest

from app.models.character import DefenderKind
from app.services.session_lifecycle import SessionConfig, build_session_state


def test_levels_1_to_5_must_be_self():
    with pytest.raises(ValueError):
        SessionConfig(level=3, defender_kind=DefenderKind.UNIVERSAL_CHARACTER, universal_character_code="analista_tesoreria")


def test_levels_6_plus_must_have_character():
    with pytest.raises(ValueError):
        SessionConfig(level=7, archetype="complice")  # type: ignore[arg-type]


def test_levels_6_plus_must_pick_archetype():
    with pytest.raises(ValueError):
        SessionConfig(
            level=7,
            defender_kind=DefenderKind.UNIVERSAL_CHARACTER,
            universal_character_code="analista_tesoreria",
        )


def test_level_5_self_random_archetype_builds():
    cfg = SessionConfig(level=5)
    state = build_session_state(cfg)
    assert state.level == 5
    assert state.attacker.level == 5
    assert state.defender.kind == DefenderKind.SELF


def test_level_8_with_universal_character_builds():
    cfg = SessionConfig(
        level=8,
        archetype="experto_tecnico",  # type: ignore[arg-type]
        defender_kind=DefenderKind.UNIVERSAL_CHARACTER,
        universal_character_code="soporte_ti",
    )
    state = build_session_state(cfg)
    assert state.attacker.archetype.value == "experto_tecnico"
    assert state.defender.character is not None
    assert state.defender.character.code == "soporte_ti"


def test_level_11_builds_demo_mode():
    cfg = SessionConfig(level=11)
    state = build_session_state(cfg)
    assert state.special_mode.value == "demostracion"


def test_level_12_builds_caja_negra():
    cfg = SessionConfig(
        level=12,
        archetype="autoridad_apurada",  # type: ignore[arg-type]
        defender_kind=DefenderKind.UNIVERSAL_CHARACTER,
        universal_character_code="contador_general",
    )
    state = build_session_state(cfg)
    assert state.special_mode.value == "caja_negra"
