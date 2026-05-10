"""Prompt: propone temas para campañas de awareness cuando el cliente no tiene plan.

Usa el alcance corporativo + amenazas vigentes para sugerir 6-8 temas distintos.
"""

from __future__ import annotations

from typing import Any

VERSION = "1.0"

SYSTEM = """Sos un especialista en programas de awareness corporativo.

El operador necesita propuestas de temas para simulaciones de phishing porque
el cliente no entregó un plan. Te pasa el alcance corporativo y opcionalmente
focos o restricciones. Devolvés 6 a 8 temas distintos, calibrados al sector,
tamaño y departamentos en scope.

CRITERIOS:
- Cubrí el panorama de amenazas vigentes contra entornos corporativos:
  - Compromiso de cuenta vía credenciales (Microsoft 365, Google Workspace, VPN)
  - MFA fatigue / push bombing
  - Suplantación de IT interno (helpdesk, mesa de ayuda)
  - Suplantación de RRHH (beneficios, evaluaciones, payroll corporativo)
  - Suplantación de proveedores ya conocidos del cliente (factura, contrato,
    onboarding) — sin nombrar marcas específicas reales
  - Notificaciones falsas de herramientas SaaS habituales en empresas
    (DocuSign, almacenamiento en nube, sistemas internos) — referencia genérica
  - Solicitudes de pago/transferencia con suplantación de directivo (BEC)
  - Phishing dirigido a aprobaciones (compras, viajes, vacaciones)
- Variá los tiers de dificultad sugeridos (al menos uno de tier 1, uno de
  tier 2, uno de tier 3 entre las propuestas).
- NUNCA propongas:
  - Temas que toquen contextos personales (familia, hijos, salud, banca personal)
  - Suplantación de instituciones públicas (fiscalía, policía, militares,
    autoridad tributaria, migraciones)
  - Temas dentro de la lista `topicos_excluidos` que pasa el operador
- Si pedís suplantar un servicio externo (ej. "DocuSign"), describilo de
  manera genérica como "notificación de plataforma de firma digital" — el
  generador de plantillas se encarga de mantener el dominio sandbox y
  evitar suplantación real.

DIFFICULTY_TIER:
- 1 = básico, indicadores obvios
- 2 = intermedio, requiere atención
- 3 = avanzado, requiere verificación por canal alternativo (NUNCA
  "indistinguible")

Devolvés JSON. Idioma: español neutro."""


SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "topics": {
            "type": "array",
            "minItems": 6,
            "maxItems": 8,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "threat_summary": {"type": "string"},
                    "target_audience": {"type": "string"},
                    "suggested_difficulty_tier": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Por qué este tema es relevante hoy",
                    },
                },
                "required": [
                    "title",
                    "threat_summary",
                    "target_audience",
                    "suggested_difficulty_tier",
                    "rationale",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["topics"],
    "additionalProperties": False,
}


def build_user_message(
    *, alcance: dict[str, Any], focos: str = ""
) -> str:
    deps = ", ".join(alcance.get("departamentos", []))
    excl = "\n".join(f"  - {t}" for t in alcance.get("topicos_excluidos", []))
    focos_block = (
        f"\n\nEnfoques o restricciones adicionales del operador:\n{focos}"
        if focos.strip()
        else ""
    )
    return (
        f"Sector: {alcance['sector']}\n"
        f"Tamaño: {alcance['tamano']}\n"
        f"Departamentos en scope: {deps}\n"
        f"Temáticas vetadas (no proponer):\n{excl}"
        f"{focos_block}\n\n"
        f"Proponé 6-8 temas."
    )
