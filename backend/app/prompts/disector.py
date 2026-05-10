"""
Prompt: disector — anota un mensaje individual con sus indicadores.

Versión: 1.0.0

Recibe un Acto (mensaje + canal + remitente). Devuelve la lista de
indicadores estructurados que el frontend usa para la "Sala de Disección":
qué fragmento resaltar y la explicación didáctica al pasar el mouse.

Esta tarea tiene tono pedagógico, no técnico-jerga.
"""
from __future__ import annotations

import json

from app.prompts._common import cabecera_sistema
from app.services.anthropic_client import GenerationResult, get_anthropic_service

VERSION = "1.0.0"


SYSTEM_PROMPT = (
    cabecera_sistema()
    + "\n\n"
    + """\
TAREA: dado un MENSAJE de un Acto (que ya fue generado o ingresado por un
facilitador), produce las anotaciones para la SALA DE DISECCIÓN.

Cada anotación es un INDICADOR detectable. Por mensaje devuelve entre 3 y 6.

Tono: didáctico, claro, sin jerga técnica innecesaria. El destinatario es un
colaborador de cualquier área, no un analista de seguridad.

Indicadores válidos (catálogo cerrado): dominio_sospechoso, urgencia_artificial,
llamado_accion_unico, autoridad_no_verificable, incongruencia_canal,
error_contexto, error_ortografia, remitente_anomalo, solicitud_datos_sensibles,
amenaza_velada, oferta_desproporcionada, enlace_acortado.

Salida: JSON estricto con esta forma:
{
  "indicadores": [
    {
      "tipo": str,                  // del catálogo de indicadores
      "fragmento": str,             // texto literal a resaltar dentro del mensaje
      "explicacion": str            // 1-2 frases en lenguaje llano
    },
    ...
  ]
}

Cada `fragmento` debe aparecer textualmente en alguno de los campos del mensaje
provisto. No inventes texto que no esté en el mensaje.
"""
)


def build_user_prompt(acto: dict) -> str:
    return f"""\
MENSAJE A DISECCIONAR:
{json.dumps(acto, ensure_ascii=False, indent=2)}

Devuelve solo el JSON con la clave "indicadores".
"""


def generar_diseccion(acto: dict, *, temperature: float = 0.3) -> GenerationResult:
    service = get_anthropic_service()
    return service.generate(
        system=SYSTEM_PROMPT,
        user=build_user_prompt(acto),
        max_tokens=2048,
        temperature=temperature,
        expect_json=True,
        contexto=f"disector@{VERSION}",
    )
