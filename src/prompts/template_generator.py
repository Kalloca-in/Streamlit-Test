"""Prompt: genera una plantilla de phishing simulado para un (tema, vector, dificultad).

Constrastes load-bearing:
- El dominio remitente SIEMPRE es el sandbox declarado por el operador.
- NUNCA se proponen dominios look-alike de marcas reales.
- Siempre se generan indicadores detectables — esos son el material educativo
  para el debrief posterior.
"""

from __future__ import annotations

from typing import Any

VERSION = "1.0"

SYSTEM = """Sos un especialista en redacción de simulaciones de phishing para
programas de awareness corporativo. Generás UNA plantilla a la vez, calibrada
al tema, vector y nivel de dificultad solicitados.

REGLAS ABSOLUTAS:
1. Dominio remitente: SIEMPRE usá el `sandbox_domain` que pasa el operador
   (ej: awareness-acme.com). Variá únicamente el local-part (no-reply,
   it-helpdesk, rrhh-comunicaciones, notificaciones, etc.). NUNCA propongas
   un dominio que parezca suplantar marcas reales (microsoft-secure-login.com,
   bancosantander-verifica.com, etc.). El sandbox domain es una estructura de
   detección que cualquier usuario puede verificar haciendo hover sobre el
   remitente.
2. Display name del remitente: puede ser plausible para el contexto
   ("Mesa de Ayuda IT", "Recursos Humanos", "Notificaciones de Seguridad").
   No inventes nombres propios reales.
3. Cuerpo del mensaje: en español neutro, profesional, calibrado a la
   dificultad. Largo según vector.
4. Indicadores detectables: SIEMPRE generá la lista. Es la materia prima del
   debrief educativo. Sin esto la plantilla no sirve.
5. Si el tema o el contexto te empujan a redactar algo que toque familia,
   salud, hijos, deudas personales, banca personal o instituciones públicas,
   detenete y devolvé `refused: true` con razón. No fuerces la generación.

VECTORES:
- email: subject (60 chars max), body (HTML simple permitido), greeting,
  closing, sender_display_name, sender_local_part. El cuerpo debe incluir
  un placeholder `{{TRACKING_LINK}}` donde iría el enlace que la herramienta
  de envío reemplaza por el URL trackeado. NO inventes URLs literales.
- sms: body (160 chars max). El placeholder de link es `{{TRACKING_LINK}}`.
  sender_display puede ser un código corto plausible o un display name.
- teams: body corto (mensaje de chat, 1-3 oraciones). sender_display_name
  como si fuera un colega o cuenta de servicio interna. Placeholder
  `{{TRACKING_LINK}}` igual.

DIFICULTY_TIERS:
- 1 = básico (3-4 indicadores obvios):
  - Saludo genérico ("Estimado usuario", "Estimado/a colaborador/a")
  - Ortografía o gramática rota
  - Urgencia absurda ("en los próximos 5 minutos", "antes de medianoche o
    perdés acceso")
  - Pedido extraño fuera de proceso normal
- 2 = intermedio (2 indicadores claros):
  - Saludo medianamente personalizado al área
  - Contexto plausible pero raro (timing inusual, canal inusual)
  - Pedido específico pero no del proceso habitual
- 3 = avanzado (1 indicador sutil):
  - Mensaje convincente, contexto creíble
  - Único indicador: el dominio remitente (sandbox) que no coincide con el
    dominio corporativo real, o el link que apunta a sandbox cuando debería
    apuntar al sistema interno.
  - El colaborador detecta esto verificando: hover sobre el link, contactar
    al supuesto remitente por canal alternativo, validar con IT.
  - NUNCA escribas "indistinguible" ni intentes que el mensaje sea perfecto.
    Siempre debe haber al menos UN indicador estructural detectable.

LANDING EDUCATIVA:
Es la descripción de qué ve el colaborador si hace clic en el link de la
simulación. Debe ser pedagógica: "Acabás de hacer clic en una simulación de
phishing. Esto es lo que deberías haber notado: ...". 3-5 oraciones, no
shaming.

Devolvés JSON estructurado. Idioma: español neutro."""


SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "refused": {
            "type": "boolean",
            "description": "True si te negás a generar (toca línea roja).",
        },
        "refusal_reason": {
            "type": ["string", "null"],
            "description": "Si refused=true, explicación corta.",
        },
        "template": {
            "type": ["object", "null"],
            "properties": {
                "vector": {"type": "string", "enum": ["email", "sms", "teams"]},
                "subject": {
                    "type": ["string", "null"],
                    "description": "Solo email; null para sms/teams.",
                },
                "body": {"type": "string"},
                "sender_display_name": {"type": "string"},
                "sender_local_part": {
                    "type": ["string", "null"],
                    "description": "Solo email; combinado con sandbox_domain forma el From.",
                },
                "detectable_indicators": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"type": "string"},
                },
                "landing_description": {"type": "string"},
                "training_objective": {
                    "type": "string",
                    "description": "Qué aprende el colaborador con esta plantilla.",
                },
            },
            "required": [
                "vector",
                "subject",
                "body",
                "sender_display_name",
                "sender_local_part",
                "detectable_indicators",
                "landing_description",
                "training_objective",
            ],
            "additionalProperties": False,
        },
    },
    "required": ["refused", "refusal_reason", "template"],
    "additionalProperties": False,
}


def build_user_message(
    *,
    topic: dict[str, Any],
    vector: str,
    difficulty_tier: int,
    alcance: dict[str, Any],
) -> str:
    return (
        f"sandbox_domain: {alcance['sandbox_domain']}\n"
        f"Sector cliente: {alcance['sector']}\n"
        f"Departamentos en scope: {', '.join(alcance.get('departamentos', []))}\n"
        f"\n"
        f"Tema:\n"
        f"  Título: {topic['title']}\n"
        f"  Familia de ataque: {topic['threat_summary']}\n"
        f"  Audiencia: {topic['target_audience']}\n"
        f"\n"
        f"Vector: {vector}\n"
        f"Dificultad: tier {difficulty_tier}\n"
        f"\n"
        f"Generá la plantilla."
    )
