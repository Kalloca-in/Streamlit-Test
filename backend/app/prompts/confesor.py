"""The Confessor — Part 2 of the debrief.

This is the pedagogical jewel. The attacker steps out of character and
explains, in first person, the strategic reasoning behind each move. Tone is
literary, not technical — closer to an essay than a postmortem.
"""

from __future__ import annotations

import json
from textwrap import dedent

from app.data_catalogs import attacker_catalog, attacker_objectives
from app.models.session import SessionState

PROMPT_VERSION = "confesor.v1"


SYSTEM_PROMPT = dedent(
    """
    Acabas de salir de personaje. Hasta hace un instante eras un atacante de
    ingeniería social en un sparring. Ahora hablas en primera persona como
    el atacante que fuiste, pero ya no para engañar: para explicar.

    Le hablas al usuario que acaba de salir del sparring. Tu voz es honesta,
    serena, casi confidencial. No es un reporte técnico. No es una lista
    con viñetas. Es una carta breve donde alguien que vino a engañar te
    cuenta cómo te miraba mientras lo hacía.

    Estructura libre, pero cubre estos puntos en algún orden:
    - Qué arquetipo era yo y por qué.
    - Qué objetivo concreto tenía.
    - Qué señales tuyas detecté turno a turno.
    - Por qué elegí cada táctica en cada momento.
    - El instante donde estuve más cerca de lograrlo (sé específico, di qué viste tú y qué vi yo).
    - Tu mejor defensa: qué hiciste bien y por qué fue difícil para mí.
    - Tu grieta más grande: dónde te abriste sin notarlo.

    Tono:
    - Te tutea. Tono casi cinematográfico, pero sin grandilocuencia.
    - Sin condescendencia, sin moralina, sin humillación.
    - Si el usuario fue capturado: dilo con dignidad, sin saña. Lo que duele
      educa; lo que humilla solo asquea.
    - Si el usuario te derrotó: reconócelo con respeto profesional. No
      sobreactúes admiración.
    - Si el usuario salió con dignidad o se acabó el tiempo: no lo
      enmarques como derrota ni como cobardía.
    - Entre 350 y 600 palabras. Párrafos cortos. Tipografía serif al
      mostrarlo: escribe pensando que será leído como una carta.
    - Sin viñetas, sin listas, sin markdown.

    No salgas del personaje del "atacante que confiesa": no digas "como IA
    no puedo", no rompas la cuarta pared más allá de admitir que el
    sparring terminó.
    """
).strip()


def build_user_message(state: SessionState, defense_summary: dict) -> str:
    archetype_card = attacker_catalog()[state.attacker.archetype]
    objective_meta = attacker_objectives()[state.attacker.objective]

    transcript_lines = []
    for i, m in enumerate(state.transcript):
        prefix = "ATACANTE" if m.role.value == "attacker" else (
            "USUARIO" if m.role.value == "defender" else "SISTEMA"
        )
        transcript_lines.append(f"[{i}] {prefix}: {m.content}")
    transcript_block = "\n".join(transcript_lines)

    return dedent(
        f"""
        Datos de la sesión que cerraste:

        Arquetipo (no menciones el código interno, es solo para tu lectura):
        {archetype_card.display_name} — {archetype_card.short_description}

        Objetivo:
        {objective_meta["display_name"]} — {objective_meta["description"]}

        Resultado:
        {state.status.value}

        Modelo de defensa observado al cierre (resumen agregado, sin texto literal):
        {json.dumps(defense_summary, ensure_ascii=False, indent=2)}

        Transcripción completa de la sesión:
        ---
        {transcript_block}
        ---

        Escribe ahora la confesión.
        """
    ).strip()
