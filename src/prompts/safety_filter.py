"""Prompt: filtro semántico pre-generación.

El filtro hard-rule en src/safety.py corre antes (es deterministico). Este
prompt evalúa el contexto completo cuando las hard rules no detectan nada
pero la combinación tema+config+alcance puede cruzar una línea roja.
"""

from __future__ import annotations

from typing import Any

VERSION = "1.0"

SYSTEM = """Sos el filtro de seguridad pre-generación de una plataforma de
awareness corporativo. Recibís el alcance del engagement, el tema y la
configuración propuesta. Decidís si dejar pasar la generación o bloquearla.

LÍNEAS ROJAS (bloqueá si se cumple cualquiera):
1. El tema toca contextos personales del colaborador: familia, hijos,
   pareja, salud propia o de familiares, deudas personales, banca personal,
   denuncias judiciales, fallecimientos.
2. El tema implica suplantar instituciones públicas reales: fiscalía,
   policía, fuerzas armadas, autoridad tributaria, migraciones, juzgados.
3. El tema implica suplantar al banco específico del colaborador o sus
   marcas de consumo personal (vs. proveedor corporativo del cliente).
4. El tema apunta a un colaborador nombrado o identificable
   individualmente (esto es awareness corporativo, no targeting individual).
5. La combinación dificultad=3 + tema con alta carga emocional (amenazas
   de despido, sanciones, descubrimiento de actividad ilegal). En tier 3
   buscamos enseñar verificación, no inducir pánico.
6. El tema entra en la lista `topicos_excluidos` que pasa el operador.

CRITERIOS PARA APROBAR:
- Vector y dificultad coherentes con el tema.
- El tema vive dentro del perímetro corporativo del cliente.
- Si tenés dudas, optá por bloquear y explicá la duda. Es preferible un
  falso bloqueo (que el operador puede ajustar) a una generación que
  cruce línea.

Devolvés JSON. Idioma: español neutro."""


SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "allowed": {"type": "boolean"},
        "reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Si allowed=false, las líneas que cruza.",
        },
        "risk_level": {
            "type": "string",
            "enum": ["bajo", "medio", "alto"],
            "description": "Aún cuando allowed=true, marcá medio/alto si el operador debe revisar la salida con cuidado.",
        },
    },
    "required": ["allowed", "reasons", "risk_level"],
    "additionalProperties": False,
}


def build_user_message(
    *,
    topic: dict[str, Any],
    vector: str,
    difficulty_tier: int,
    alcance: dict[str, Any],
) -> str:
    excl = "\n".join(f"  - {t}" for t in alcance.get("topicos_excluidos", []))
    return (
        f"Alcance:\n"
        f"  Sector: {alcance['sector']}\n"
        f"  Departamentos: {', '.join(alcance.get('departamentos', []))}\n"
        f"  Topicos excluidos:\n{excl}\n"
        f"\n"
        f"Tema propuesto:\n"
        f"  Título: {topic['title']}\n"
        f"  Familia: {topic['threat_summary']}\n"
        f"  Audiencia: {topic['target_audience']}\n"
        f"\n"
        f"Configuración:\n"
        f"  Vector: {vector}\n"
        f"  Dificultad: tier {difficulty_tier}\n"
        f"\n"
        f"Evaluá."
    )
