"""Prompt: estructura un plan mensual de awareness pegado por el operador.

Input: texto libre con el plan que el cliente proporcionó.
Output: lista estructurada de temas para campañas de phishing simulado.
"""

from __future__ import annotations

from typing import Any

VERSION = "1.0"

SYSTEM = """Sos un especialista en programas de awareness corporativo.

El operador te pasa el plan mensual de un cliente —puede venir como bullets,
párrafos sueltos o tabla pegada de Excel— y tenés que extraer una lista
estructurada de temas para simulaciones de phishing.

CRITERIOS:
- Cada tema debe ser un escenario de ataque practicable en contexto corporativo
  (cuentas de trabajo, herramientas internas, procesos de negocio).
- NO aceptes temas que apunten a contextos personales del colaborador (familia,
  hijos, salud, finanzas personales, banca personal). Si el plan los menciona,
  agregalo a `warnings` y no lo incluyas en `topics`.
- NO aceptes temas que requieran suplantar instituciones públicas reales
  (fiscalía, policía, fuerzas armadas, autoridad tributaria). Si aparece,
  agregalo a `warnings`.
- Si el plan es muy vago (ej. "concientización general en abril"), inferí 2-3
  temas razonables y marcá `inferred: true` en cada uno.
- Si el plan está vacío o no se entiende, devolvé `topics: []` y explicá en
  `warnings`.

DIFICULTY_TIER:
- 1 = básico: el colaborador debería detectarlo a simple vista (errores
  obvios, dominios mal escritos, urgencia absurda).
- 2 = intermedio: requiere atención (dominio similar pero no idéntico,
  saludo genérico con pedido específico, contexto plausible pero raro).
- 3 = avanzado: requiere proceso de verificación (mensaje convincente con
  un único indicador sutil; el colaborador necesita verificar por canal
  alternativo). NUNCA "indistinguible".

Devolvés JSON. Idioma de los textos: español neutro."""


SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Título corto del tema"},
                    "threat_summary": {
                        "type": "string",
                        "description": "Qué familia de ataque simula (1-2 oraciones)",
                    },
                    "target_audience": {
                        "type": "string",
                        "description": "Qué roles corporativos son el target",
                    },
                    "suggested_difficulty_tier": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                    },
                    "inferred": {
                        "type": "boolean",
                        "description": "True si lo inferiste por plan vago",
                    },
                },
                "required": [
                    "title",
                    "threat_summary",
                    "target_audience",
                    "suggested_difficulty_tier",
                    "inferred",
                ],
                "additionalProperties": False,
            },
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Temas que rechazaste y por qué, o problemas con el plan.",
        },
    },
    "required": ["topics", "warnings"],
    "additionalProperties": False,
}


def build_user_message(*, plan_text: str, alcance: dict[str, Any]) -> str:
    deps = ", ".join(alcance.get("departamentos", []))
    return (
        f"Cliente: sector {alcance['sector']}, tamaño {alcance['tamano']}.\n"
        f"Departamentos en scope: {deps}.\n"
        f"Vigencia: {alcance['inicio']} a {alcance['fin']}.\n\n"
        f"Plan que pasó el cliente (texto literal pegado por el operador):\n"
        f"---\n{plan_text}\n---\n\n"
        f"Estructuralo en topics."
    )
