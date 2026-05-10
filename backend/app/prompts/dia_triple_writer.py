"""
Prompt: escritor del Día Triple.

Versión: 1.0.0

Recibe:
- personaje (dict con datos del personaje)
- gancho psicológico raíz
- nivel de dificultad (1-3)

Devuelve JSON con la forma de DiaTripleCreate (los tres actos + indicadores
+ nota de revelación). El acto-1 es CIUDADANO (mañana), acto-2 es
COLABORADOR (mediodía), acto-3 es CLIENTE (tarde/noche).
"""
from __future__ import annotations

import json

from app.core.enums import GanchoPsicologico, NivelDificultad
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
TAREA: producir un "DÍA TRIPLE" — tres dramatizaciones de spearphishing
contra el MISMO personaje ficticio, una por cada rol del día:

  ACTO 1 — 07:30 — Rol CIUDADANO (SMS / WhatsApp / app pública)
  ACTO 2 — 11:00 — Rol COLABORADOR (correo o canal interno de su empresa)
  ACTO 3 — 19:00 — Rol CLIENTE (banco, retailer, streaming u otro consumo)

Los tres actos deben:
- Compartir EXACTAMENTE el mismo gancho psicológico raíz, declarado en input.
- Diferir en superficie (canal, marca, pretexto), ser idénticos en estructura.
- Llevar entre 3 y 6 indicadores detectables cada uno (catálogo cerrado).
- Mantenerse al nivel de dificultad indicado, sin pasarlo.
- Usar SOLO marcas del catálogo, por slug.

Indicadores válidos (catálogo cerrado): dominio_sospechoso, urgencia_artificial,
llamado_accion_unico, autoridad_no_verificable, incongruencia_canal,
error_contexto, error_ortografia, remitente_anomalo, solicitud_datos_sensibles,
amenaza_velada, oferta_desproporcionada, enlace_acortado.

Canales válidos: sms, whatsapp, correo, llamada, app_notificacion.

Roles: ciudadano, colaborador, cliente.

Salida: JSON estricto con esta forma exacta:

{
  "titulo": str,
  "gancho_psicologico_raiz": str,
  "nivel_dificultad": int,
  "nota_revelacion": str,                // golpe pedagógico de cierre
  "actos": [
    {
      "orden": 1,
      "rol": "ciudadano",
      "canal": str,
      "hora_dramatizada": "HH:MM",
      "remitente_aparente": str,
      "asunto": str | null,
      "cuerpo": str,
      "marca_ficticia_slug": str | null,
      "opciones_decision": [
        {"id": "a", "texto": str, "consecuencia": str, "es_segura": bool},
        {"id": "b", "texto": str, "consecuencia": str, "es_segura": bool},
        {"id": "c", "texto": str, "consecuencia": str, "es_segura": bool}
      ],
      "indicadores": [
        {"tipo": str, "fragmento": str, "explicacion": str},
        ...
      ]
    },
    { ... acto 2 colaborador ... },
    { ... acto 3 cliente ... }
  ]
}

REGLAS extra:
- Cada `indicadores[].fragmento` debe aparecer textualmente dentro de `cuerpo`,
  `asunto` o `remitente_aparente` del mismo acto.
- Al menos UNA `opcion_decision` por acto debe ser "es_segura": true.
- `nota_revelacion` debe nombrar el gancho raíz y articular por qué los tres
  actos lo comparten.
- No uses datos personales del usuario real bajo ningún concepto.
"""
)


def build_user_prompt(
    personaje: dict,
    gancho: GanchoPsicologico,
    nivel: NivelDificultad,
) -> str:
    techo = techo_dificultad()
    catalogo = render_catalogo_marcas()
    return f"""\
PERSONAJE (sólo lectura; basa los tres actos en él):
{json.dumps(personaje, ensure_ascii=False, indent=2)}

GANCHO PSICOLÓGICO RAÍZ a usar en los tres actos: {gancho.value}
NIVEL de dificultad: {int(nivel)} (techo absoluto: {techo})

CATÁLOGO DE MARCAS FICTICIAS (única fuente permitida):
{catalogo}

Devuelve solo el JSON del Día Triple.
"""


def generar_dia_triple(
    personaje: dict,
    gancho: GanchoPsicologico,
    nivel: NivelDificultad,
    *,
    temperature: float = 0.55,
) -> GenerationResult:
    service = get_anthropic_service()
    return service.generate(
        system=SYSTEM_PROMPT,
        user=build_user_prompt(personaje, gancho, nivel),
        max_tokens=4096,
        temperature=temperature,
        expect_json=True,
        contexto=f"dia_triple_writer@{VERSION}",
    )
