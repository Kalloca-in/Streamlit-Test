"""Round-trip tests for the in-memory session models."""

from __future__ import annotations

import pytest

from app.models.attacker import (
    AttackerArchetype,
    AttackerInstance,
    AttackerObjective,
)
from app.models.character import CharacterCard, DefenderIdentity, DefenderKind
from app.models.defense import DefenseModel, PsychHook, StressSignal, TurnObservation
from app.models.session import (
    SessionState,
    SessionStatus,
    TurnMessage,
    TurnRole,
)


def test_defender_identity_requires_character_when_not_self():
    with pytest.raises(ValueError):
        DefenderIdentity(kind=DefenderKind.UNIVERSAL_CHARACTER)


def test_defense_model_aggregates_observations():
    d = DefenseModel(session_id="x")
    d.apply(
        TurnObservation(
            turn=1,
            hooks_resisted=[PsychHook.AUTORIDAD],
            hooks_accepted=[PsychHook.RECIPROCIDAD],
            stress_signal=StressSignal.HESITATION,
            is_critical_moment=True,
        )
    )
    d.apply(
        TurnObservation(
            turn=2,
            hooks_resisted=[PsychHook.AUTORIDAD],
        )
    )
    assert d.turns_observed == 2
    assert d.hook_resist_counts[PsychHook.AUTORIDAD] == 2
    assert d.hook_accept_counts[PsychHook.RECIPROCIDAD] == 1
    assert d.critical_moments == [1]


def test_session_state_roundtrip():
    s = SessionState(
        session_id="abc",
        level=5,
        attacker=AttackerInstance(
            archetype=AttackerArchetype.COMPLICE,
            objective=AttackerObjective.EXTRACT_SENSITIVE_DATA,
            level=5,
        ),
        defender=DefenderIdentity(
            kind=DefenderKind.UNIVERSAL_CHARACTER,
            character=CharacterCard(
                code="analista_tesoreria",
                display_name="Marta",
                role_title="Analista de Tesorería",
                exposure_profile="medio",
            ),
        ),
    )
    s.append(TurnMessage(role=TurnRole.ATTACKER, content="hola"))
    s.append(TurnMessage(role=TurnRole.DEFENDER, content="quién eres"))
    s.status = SessionStatus.ACTIVE

    raw = s.model_dump_json()
    s2 = SessionState.model_validate_json(raw)
    assert s2.turn_count == 2
    assert s2.attacker.archetype == AttackerArchetype.COMPLICE
    assert s2.defender.character.display_name == "Marta"
