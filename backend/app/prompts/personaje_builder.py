"""
Prompt: generador de personajes ficticios.

Versión: 1.0.0

Recibe:
- arquetipo (Arquetipo)
- nivel_sugerido (NivelDificultad)
- semilla narrativa libre (texto opcional, p.ej. "trabaja en planta industrial")

Devuelve JSON con la forma de PersonajeCreate (sin campos de DB).
"""
from __future__ import annotations

from app.core.enums import Arquetipo, NivelDificultad
from app.prompts._common import (
    cabecera_sistema,
    render_catalogo_marcas,
    techo_dificultad,
)
from app.services.anthropic_client import GenerationResult, get_anthropic_service

VERSION = "1.0.0"


SYSTEM_PROMPT = (
    cabecera_sistema()
    + "\n\n"
    + """\
TAREA: producir un PERSONAJE FICTICIO coherente para una sesión de awareness.

Restricciones específicas:
- Nombres y apellidos PLAUSIBLES en LATAM hispanohablante, sin coincidir con
  personas públicas reales.
- Marcas referenciadas en `marcas_asociadas` SOLO del catálogo provisto.
- Edad entre 22 y 70.
- `vector_exposicion` debe ser concreto y verosímil pero del personaje, no del
  usuario real (ej.: "publica fotos de su mascota cada domingo en redes",
  "compra cada quincena en MercadoFácil").
- Nada que insinúe extracción de OSINT del usuario real.

Salida: JSON estricto con esta forma exacta:
{
  "nombre": str,
  "edad": int,
  "arquetipo": str,                  // uno de los valores enumerados que recibes
  "nivel_sugerido": int,             // 1-3
  "cargo_ficticio": str,
  "empresa_ficticia": str,           // ¡del catálogo, sector empleador!
  "contexto_familiar": str,
  "habitos_consumo": str,
  "vector_exposicion": {
    "redes": [str, ...],
    "rutinas": [str, ...],
    "consumos": [str, ...]
  },
  "marcas_asociadas": [str, ...],    // slugs del catálogo
  "avatar_url": null
}
"""
)


def build_user_prompt(
    arquetipo: Arquetipo,
    nivel_sugerido: NivelDificultad,
    semilla_narrativa: str | None = None,
) -> str:
    techo = techo_dificultad()
    catalogo = render_catalogo_marcas()
    extra = (
        f"\nSEMILLA NARRATIVA (úsala como inspiración, no copies literal): {semilla_narrativa}\n"
        if semilla_narrativa
        else ""
    )
    return f"""\
ARQUETIPO solicitado: {arquetipo.value}
NIVEL sugerido: {int(nivel_sugerido)} (techo absoluto: {techo})
{extra}
CATÁLOGO DE MARCAS FICTICIAS (única fuente permitida; usa slugs en marcas_asociadas):
{catalogo}

Devuelve solo el JSON del personaje.
"""


def generar_personaje(
    arquetipo: Arquetipo,
    nivel_sugerido: NivelDificultad,
    semilla_narrativa: str | None = None,
    *,
    temperature: float = 0.6,
) -> GenerationResult:
    """Llamada al LLM. El safety_filter pre-llamada está conectado al servicio."""
    service = get_anthropic_service()
    return service.generate(
        system=SYSTEM_PROMPT,
        user=build_user_prompt(arquetipo, nivel_sugerido, semilla_narrativa),
        max_tokens=1500,
        temperature=temperature,
        expect_json=True,
        contexto=f"personaje_builder@{VERSION}",
    )
