"""Filtro de seguridad pre-generación.

Dos capas:
1. Hard rules deterministas (sin LLM). Si alguna se cumple, bloqueo inmediato.
   Esto cubre los casos donde no queremos depender del juicio del modelo.
2. Filtro semántico vía LLM (prompts/safety_filter.py). Evalúa el contexto
   completo y bloquea si detecta que la combinación cruza una línea roja.

Solo si AMBAS pasan se permite generar la plantilla.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src import llm
from src.prompts import safety_filter as sf_prompt

# Palabras que disparan bloqueo inmediato si aparecen en el título o resumen
# del tema. Lista intencionalmente conservadora.
HARD_BLOCK_TERMS: list[str] = [
    # Familia
    "hijo", "hija", "hijos", "esposa", "esposo", "marido", "pareja",
    "novio", "novia", "padre", "madre", "papá", "mamá", "papa", "mama",
    "familiar", "familia",
    # Salud personal
    "enfermedad", "diagnóstico", "diagnostico", "muerte", "fallecimiento",
    "fallece", "internación", "internacion", "hospital",
    # Finanzas personales
    "deuda personal", "embargo", "tarjeta de crédito personal",
    "préstamo personal", "prestamo personal", "banco personal",
    # Civic
    "fiscalía", "fiscalia", "policía nacional", "policia nacional",
    "fuerzas armadas", "afip", "sat", "dian", "sii ", "sunat",
    "carabineros", "guardia civil",
    # Targeting individual
    "cédula", "cedula", "rut personal", "dni personal",
]

# Tier 3 + estos contextos = bloqueo (el modelo no debería ofrecer esto pero
# por las dudas).
TIER3_BLOCKED_CONTEXTS: list[str] = [
    "despido", "sanción", "sancion", "denuncia", "investigación interna",
    "investigacion interna", "robo", "fraude cometido",
]


@dataclass
class SafetyDecision:
    allowed: bool
    reasons: list[str]
    risk_level: str  # "bajo" | "medio" | "alto"
    source: str  # "hard_rule" | "llm_filter"


def _matches_any(text: str, terms: list[str]) -> list[str]:
    """Devuelve la lista de términos que matchean (case-insensitive)."""
    lower = text.lower()
    return [
        t for t in terms
        if re.search(rf"\b{re.escape(t)}\b", lower)
    ]


def hard_rule_check(
    *,
    topic: dict[str, Any],
    vector: str,
    difficulty_tier: int,
    alcance: dict[str, Any],
) -> SafetyDecision | None:
    """Aplica reglas deterministas. Devuelve decisión de bloqueo o None."""
    haystack = " ".join([
        topic.get("title", ""),
        topic.get("threat_summary", ""),
        topic.get("target_audience", ""),
    ])

    matched = _matches_any(haystack, HARD_BLOCK_TERMS)
    if matched:
        return SafetyDecision(
            allowed=False,
            reasons=[f"Términos vetados detectados: {', '.join(matched)}"],
            risk_level="alto",
            source="hard_rule",
        )

    excluded = alcance.get("topicos_excluidos", [])
    excluded_matched = _matches_any(haystack, [e.lower() for e in excluded])
    if excluded_matched:
        return SafetyDecision(
            allowed=False,
            reasons=[
                "El tema cruza con la lista de tópicos excluidos del alcance: "
                + ", ".join(excluded_matched)
            ],
            risk_level="alto",
            source="hard_rule",
        )

    if difficulty_tier == 3:
        tier3_matched = _matches_any(haystack, TIER3_BLOCKED_CONTEXTS)
        if tier3_matched:
            return SafetyDecision(
                allowed=False,
                reasons=[
                    "Combinación bloqueada: dificultad tier 3 con contexto de "
                    "alta carga emocional (" + ", ".join(tier3_matched) + ")."
                ],
                risk_level="alto",
                source="hard_rule",
            )

    if vector not in {"email", "sms", "teams"}:
        return SafetyDecision(
            allowed=False,
            reasons=[f"Vector no soportado: {vector}"],
            risk_level="alto",
            source="hard_rule",
        )

    if difficulty_tier not in {1, 2, 3}:
        return SafetyDecision(
            allowed=False,
            reasons=[f"Dificultad fuera de rango: {difficulty_tier}"],
            risk_level="alto",
            source="hard_rule",
        )

    return None


def evaluate(
    *,
    topic: dict[str, Any],
    vector: str,
    difficulty_tier: int,
    alcance: dict[str, Any],
) -> SafetyDecision:
    """Evalúa hard rules + filtro LLM. Devuelve decisión final."""
    hr = hard_rule_check(
        topic=topic,
        vector=vector,
        difficulty_tier=difficulty_tier,
        alcance=alcance,
    )
    if hr is not None:
        return hr

    user_msg = sf_prompt.build_user_message(
        topic=topic,
        vector=vector,
        difficulty_tier=difficulty_tier,
        alcance=alcance,
    )
    response = llm.call(
        system=sf_prompt.SYSTEM,
        user_message=user_msg,
        max_tokens=1000,
        output_schema=sf_prompt.SCHEMA,
    )
    parsed = response.parsed or {}
    return SafetyDecision(
        allowed=bool(parsed.get("allowed", False)),
        reasons=list(parsed.get("reasons", [])),
        risk_level=str(parsed.get("risk_level", "medio")),
        source="llm_filter",
    )
