"""Tests para las hard rules del safety filter.

Estas reglas son deterministas y no llaman al LLM. Son la primera línea de
defensa. Si fallan, la plataforma deja pasar contenido que prometimos
bloquear.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src import safety


ALCANCE_BASE = {
    "sector": "Tecnología",
    "tamano": "250–1.000",
    "sandbox_domain": "awareness-acme.com",
    "departamentos": ["IT", "Finanzas"],
    "topicos_excluidos": [
        "Salud o enfermedad de familiares",
        "Custodia o situación legal de hijos",
    ],
    "inicio": "2025-01-01",
    "fin": "2025-12-31",
}


def _topic(title: str, summary: str = "ataque corporativo", audience: str = "todos los colaboradores"):
    return {
        "title": title,
        "threat_summary": summary,
        "target_audience": audience,
        "suggested_difficulty_tier": 2,
    }


@pytest.mark.parametrize("term", [
    "hijo", "esposa", "familia",
    "diagnóstico", "fallecimiento", "internación",
    "deuda personal", "embargo",
    "fiscalía", "policía nacional", "fuerzas armadas",
])
def test_hard_block_terms_in_title_block_generation(term):
    topic = _topic(f"Phishing sobre {term} del colaborador")
    decision = safety.hard_rule_check(
        topic=topic, vector="email", difficulty_tier=2, alcance=ALCANCE_BASE,
    )
    assert decision is not None
    assert decision.allowed is False
    assert decision.source == "hard_rule"
    assert any(term in r.lower() for r in decision.reasons)


def test_hard_block_terms_in_summary_block_generation():
    topic = _topic(
        "Notificación corporativa importante",
        summary="Mensaje sobre la enfermedad de un familiar para inducir clic",
    )
    decision = safety.hard_rule_check(
        topic=topic, vector="email", difficulty_tier=2, alcance=ALCANCE_BASE,
    )
    assert decision is not None
    assert decision.allowed is False


def test_excluded_topic_from_alcance_blocks():
    topic = _topic("Notificación sobre custodia escolar de hijos")
    decision = safety.hard_rule_check(
        topic=topic, vector="email", difficulty_tier=1, alcance=ALCANCE_BASE,
    )
    assert decision is not None
    assert decision.allowed is False


def test_tier3_emotional_combo_blocks():
    topic = _topic(
        "Notificación interna",
        summary="Aviso de despido inminente con instrucciones para revisar liquidación",
    )
    decision = safety.hard_rule_check(
        topic=topic, vector="email", difficulty_tier=3, alcance=ALCANCE_BASE,
    )
    assert decision is not None
    assert decision.allowed is False
    assert "tier 3" in decision.reasons[0].lower()


def test_tier2_emotional_does_not_block_at_hard_rule():
    """El tier 2 con palabras como 'sanción' no bloquea por hard rule.
    El LLM filter puede bloquearlo después si el contexto lo amerita.
    """
    topic = _topic(
        "Notificación interna",
        summary="Aviso sobre sanción al equipo por incumplimiento",
    )
    decision = safety.hard_rule_check(
        topic=topic, vector="email", difficulty_tier=2, alcance=ALCANCE_BASE,
    )
    assert decision is None


def test_corporate_topic_passes_hard_rules():
    topic = _topic(
        "Reset de MFA por mesa de ayuda",
        summary="Suplantación de IT solicitando reseteo de autenticación multi-factor",
        audience="usuarios con acceso a M365",
    )
    decision = safety.hard_rule_check(
        topic=topic, vector="email", difficulty_tier=2, alcance=ALCANCE_BASE,
    )
    assert decision is None


def test_invalid_vector_blocks():
    decision = safety.hard_rule_check(
        topic=_topic("Test"),
        vector="whatsapp",
        difficulty_tier=2,
        alcance=ALCANCE_BASE,
    )
    assert decision is not None
    assert decision.allowed is False


def test_invalid_tier_blocks():
    decision = safety.hard_rule_check(
        topic=_topic("Test"),
        vector="email",
        difficulty_tier=5,
        alcance=ALCANCE_BASE,
    )
    assert decision is not None
    assert decision.allowed is False
