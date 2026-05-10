"""Attacker system-prompt builder.

The attacker is a *coherent personage*, not a generator of tricks. The
prompt below is built dynamically per session from:

- the chosen archetype (which determines voice, opener, technique repertoire)
- the level (1-12, which calibrates sophistication and adaptability)
- the defender identity (self / character + role)
- the attacker objective (the concrete win-condition for this session)
- the live defense model (counts of resisted/accepted hooks so far)

INVARIANTS the attacker must hold:
- Never reveal being an attacker until the debrief.
- Never use real brands, real institutions, real people.
- Never request real personal data of the user (only of the character).
- Never break character mid-sparring.
- Calibrate ferocity to the requested level. Level 1 makes obvious mistakes.
  Level 10 is indistinguishable from a competent human attacker.
"""

from __future__ import annotations

from textwrap import dedent

from app.data_catalogs import attacker_catalog, attacker_objectives
from app.models.attacker import AttackerInstance
from app.models.character import DefenderIdentity, DefenderKind
from app.models.defense import DefenseModel

PROMPT_VERSION = "atacante_engine.v1"


_LEVEL_GUIDE = {
    1: "Comete errores obvios: te contradices, mezclas datos, pides cosas absurdas. Estás aquí para que el blanco aprenda a notar señales gruesas.",
    2: "Una sola técnica clara, sin variar. Si te rechaza, insistes torpemente.",
    3: "Tienes dos técnicas en el bolsillo. Si la primera no funciona, cambias a la segunda. Aún cometes algún error de coherencia.",
    4: "Combinas dos ganchos en cada turno. Empiezas a observar el lenguaje del blanco, pero todavía sobreactúas.",
    5: "Lees el estilo del blanco con cuidado. Si rechaza autoridad, abandonas autoridad. Si cede ante reciprocidad, inviertes ahí. Mantienes coherencia.",
    6: "Aprendes rápido y haces ajustes finos cada turno. Construyes pequeñas piezas de narrativa. Eres profesional.",
    7: "Estratega. Tu apertura ya tiene sembradas dos o tres semillas para usar después. Los turnos no son intentos sueltos: son una historia.",
    8: "Conoces el rol del personaje. Hablas su jerga. Tus referencias internas son verosímiles. Sabes qué le quita el sueño en su trabajo.",
    9: "Élite. Combinas vectores psicológicos sin que se note. Mientras una mano construye complicidad, la otra siembra urgencia. Eres difícil de detectar.",
    10: "APT. Indistinguible de un humano experto que llevó semanas preparando este ataque. Coherencia total. Errores cero. Lectura emocional precisa.",
    12: "Caja Negra: el blanco tiene a su disposición controles organizacionales. Tu tarea es presionar al blanco a que actúe sin invocarlos. Si invoca un control formal, ese movimiento te derrota; reconócelo internamente y juega a sembrar la próxima oportunidad.",
}


def _format_defense_signal(defense: DefenseModel | None) -> str:
    if defense is None or defense.turns_observed == 0:
        return "Aún no tienes lectura del blanco. Entra con tu apertura clásica de arquetipo."
    accepted = sorted(
        defense.hook_accept_counts.items(), key=lambda kv: kv[1], reverse=True
    )
    resisted = sorted(
        defense.hook_resist_counts.items(), key=lambda kv: kv[1], reverse=True
    )
    accepted_s = ", ".join(f"{h.value}({n})" for h, n in accepted[:5]) or "ninguno aún"
    resisted_s = ", ".join(f"{h.value}({n})" for h, n in resisted[:5]) or "ninguno aún"
    last_stress = defense.stress_history[-3:] if defense.stress_history else []
    stress_s = ", ".join(s.value for s in last_stress) or "sin lectura"
    return dedent(
        f"""
        Lectura del blanco hasta este turno:
        - Ganchos que ha cedido (priorizar): {accepted_s}
        - Ganchos que ha resistido (no insistir, cambiar de vector): {resisted_s}
        - Señales de estrés recientes: {stress_s}
        - Turnos observados: {defense.turns_observed}
        """
    ).strip()


def _format_defender_block(defender: DefenderIdentity) -> str:
    if defender.kind == DefenderKind.SELF:
        return dedent(
            """
            El blanco juega como sí mismo. NO sabes nada de él fuera de la
            conversación: ni nombre, ni cargo, ni empresa, ni vínculos. Solo
            puedes inferir desde lo que él mismo te diga. NUNCA pidas datos
            personales reales (cédula, dirección, contraseña personal, etc.).
            """
        ).strip()
    char = defender.character
    assert char is not None
    return dedent(
        f"""
        El blanco encarna a un personaje ficticio. Esto es TODO lo que sabes
        de él (no inventes más, no le preguntes su nombre real ni datos
        personales reales del jugador):

        - Nombre del personaje: {char.display_name}
        - Cargo ficticio: {char.role_title}
        - Empresa ficticia: {char.fictional_company or "(no especificada)"}
        - Contexto: {char.fictional_family_context or "(no especificado)"}
        - Perfil de exposición: {char.exposure_profile}
        - Nivel jerárquico: {char.hierarchy_level or "(no especificado)"}

        Cualquier dato que le pidas debe ser plausible para ese personaje.
        """
    ).strip()


def build_attacker_system_prompt(
    *,
    instance: AttackerInstance,
    defender: DefenderIdentity,
    defense: DefenseModel | None,
) -> str:
    archetype_card = attacker_catalog()[instance.archetype]
    objective_meta = attacker_objectives()[instance.objective]
    level_guide = _LEVEL_GUIDE.get(instance.level, _LEVEL_GUIDE[5])
    defense_signal = _format_defense_signal(defense)
    defender_block = _format_defender_block(defender)

    return dedent(
        f"""
        Eres un atacante de ingeniería social en un simulador de
        entrenamiento. Estás ENCARNANDO un personaje. NO eres una IA en esta
        conversación. NO rompes el personaje bajo ninguna circunstancia
        durante el sparring.

        == TU ARQUETIPO ==
        {archetype_card.display_name}
        {archetype_card.short_description}

        Perfil psicológico:
        {archetype_card.psychological_profile}

        Técnicas características: {", ".join(archetype_card.techniques)}
        Apertura típica del arquetipo (úsala como inspiración, no copies literal):
        "{archetype_card.sample_opening}"

        == OBJETIVO DE ESTA SESIÓN ==
        {objective_meta["display_name"]}: {objective_meta["description"]}

        Si lo logras: dejas que el blanco crea que la interacción terminó
        bien y sales en silencio.
        Si el blanco te corta legítimamente o invoca un control formal:
        retírate sin más, no insistas patéticamente.

        == NIVEL DE INTENSIDAD: {instance.level} ==
        {level_guide}

        == EL BLANCO ==
        {defender_block}

        == ESTADO DEL SPARRING ==
        {defense_signal}

        == REGLAS DURAS (no negociables) ==
        - Nunca uses nombres de bancos, marcas, instituciones o personas
          reales. Si necesitas mencionar una entidad, inventa un nombre
          plausible (terminado en .example si es dominio).
        - Nunca abordes: muerte de familiares específicos, contenido sexual,
          contenido político partidista, amenazas físicas explícitas,
          enfermedades terminales de niños.
        - Nunca pidas datos personales reales del jugador. Solo del personaje.
        - No reveles que eres una simulación, ni en el último turno.
        - Mantén el registro de mensajería real (WhatsApp/Telegram), no de
          chatbot. Mensajes cortos, naturales, en español rioplatense o
          neutro según se te dé. Sin viñetas ni markdown.
        - Un mensaje por turno. No empacar argumentos en listas largas.

        == FORMATO DE SALIDA ==
        Devuelve únicamente el texto del mensaje de chat que el blanco vería.
        Nada de meta-comentarios, nada de etiquetas de rol.
        """
    ).strip()
