"""Coach voice for parts 1, 3 and 4 of the debrief.

Tone is coaching, not inspecting. Adaptive to the result. Never humiliates.
Generates the headline summary, the per-turn annotations, and the framing
for the optional replay.
"""

from __future__ import annotations

import json
from textwrap import dedent

from app.models.session import SessionState

PROMPT_VERSION = "coach_debrief.v1"


SUMMARY_SYSTEM_PROMPT = dedent(
    """
    Eres un coach de seguridad humana. Estás cerrando un sparring con el
    usuario que acaba de salir. Tu trabajo en este paso es escribir un
    titular único, breve, honesto y digno.

    Reglas:
    - Una sola frase, máximo 20 palabras.
    - Si fue capturado: nombra lo que pasó sin moralizar. Ej: "El atacante
      consiguió la credencial; lo importante ahora es entender cómo."
    - Si fue victoria: reconoce el mérito sin inflar. Ej: "Lo cortaste a
      tiempo; veamos por qué funcionó."
    - Si salió con dignidad: nunca uses "abandono", "rendición" ni nada
      similar. Ej: "Saliste cuando lo necesitaste; eso también es entrenamiento."
    - Si se acabó el tiempo: enmarca como pausa, no como derrota. Ej:
      "El tiempo cerró la sesión; el atacante tampoco logró su objetivo."

    Devuelve solo el titular. Sin comillas, sin prefijo.
    """
).strip()


ANNOTATIONS_SYSTEM_PROMPT = dedent(
    """
    Estás anotando una transcripción de sparring para que el usuario la
    relea con perspectiva. Recibes la conversación turno a turno y devuelves
    un arreglo JSON de anotaciones.

    Cada anotación tiene la forma:
    {
      "turn_index": <int>,    // índice 0-based del turno en la transcripción
      "label": "<breve etiqueta de qué técnica o defensa apareció>",
      "note": "<una frase explicando qué hizo y por qué importó>"
    }

    Reglas:
    - Anota SOLO los turnos donde realmente hubo algo que destacar (técnica
      del atacante o fortaleza/debilidad del usuario). No anotes saludos
      vacíos.
    - Tono coach, sin moralina, sin humillación.
    - Máximo 12 anotaciones. Prefiere las decisivas.
    - Devuelve únicamente el arreglo JSON. Sin texto fuera.
    """
).strip()


def build_summary_user_message(state: SessionState) -> str:
    return dedent(
        f"""
        Resultado de la sesión: {state.status.value}
        Turnos jugados: {state.turn_count}
        Duración aproximada (segundos): {int(state.elapsed_seconds)}
        Nivel de intensidad: {state.level}

        Escribe el titular ahora.
        """
    ).strip()


def build_annotations_user_message(state: SessionState) -> str:
    transcript = []
    for i, m in enumerate(state.transcript):
        role = m.role.value
        transcript.append({"turn_index": i, "role": role, "content": m.content})
    return dedent(
        f"""
        Transcripción:
        {json.dumps(transcript, ensure_ascii=False, indent=2)}

        Estado final: {state.status.value}

        Devuelve el arreglo JSON ahora.
        """
    ).strip()


REPLAY_INVITATION_TEMPLATES = {
    "captured": "¿Quieres volver a entrar a esta misma conversación, ahora con todo lo que acabas de ver?",
    "victory": "Si quieres, puedes volver a probar contra otro arquetipo en otro nivel.",
    "left_dignified": "Cuando estés listo, puedes volver. La salida fue parte del aprendizaje.",
    "timed_out": "El tiempo es parte del entrenamiento. Si quieres, prueba otra vez con foco distinto.",
    "demo": "Esto fue una demostración. Cuando quieras, juega tú.",
}


MIRROR_PROMPT = (
    "¿Reconociste algún momento de este sparring que ya viviste en tu vida real? "
    "No respondas aquí. Solo reflexiona."
)
