"""Sección 5: Generación de plantillas.

Para cada tema seleccionado, el operador elige vector + dificultad y genera
una plantilla. Antes de generar, corre el safety filter (hard rules + LLM).
Las plantillas generadas se acumulan en session_state.generacion['templates'].
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st

from src import llm, safety, state
from src.prompts import template_generator

VECTORES = ["email", "sms", "teams"]
TIERS = [1, 2, 3]
TIER_LABELS = {
    1: "Tier 1 — Básico (indicadores obvios)",
    2: "Tier 2 — Intermedio (requiere atención)",
    3: "Tier 3 — Avanzado (requiere verificación)",
}


def _ensure_state() -> dict[str, Any]:
    g = st.session_state.get("generacion")
    if not g:
        g = {"templates": [], "generating": None, "last_decision": None, "last_error": None}
        st.session_state.generacion = g
    return g


def _topic_card(idx: int, topic: dict[str, Any], alcance: dict[str, Any]) -> None:
    g = _ensure_state()
    with st.container(border=True):
        st.markdown(f"**Tema {idx + 1}: {topic['title']}**")
        st.caption(topic["threat_summary"])
        st.caption(f"Audiencia: {topic['target_audience']}")

        with st.form(f"gen_form_{idx}", clear_on_submit=False):
            cols = st.columns([1, 1, 1])
            with cols[0]:
                vector = st.selectbox(
                    "Vector",
                    VECTORES,
                    key=f"vec_{idx}",
                )
            with cols[1]:
                tier = st.selectbox(
                    "Dificultad",
                    TIERS,
                    index=TIERS.index(topic.get("suggested_difficulty_tier", 2)),
                    format_func=lambda t: TIER_LABELS[t],
                    key=f"tier_{idx}",
                )
            with cols[2]:
                st.markdown("")
                st.markdown("")
                submitted = st.form_submit_button(
                    "Generar plantilla", type="primary", use_container_width=True
                )

        if submitted:
            _run_generation(topic_idx=idx, topic=topic, vector=vector, tier=tier, alcance=alcance)
            st.rerun()


def _run_generation(
    *,
    topic_idx: int,
    topic: dict[str, Any],
    vector: str,
    tier: int,
    alcance: dict[str, Any],
) -> None:
    g = _ensure_state()
    g["last_error"] = None
    g["last_decision"] = None

    with st.spinner("Evaluando seguridad..."):
        try:
            decision = safety.evaluate(
                topic=topic, vector=vector, difficulty_tier=tier, alcance=alcance
            )
        except llm.LLMError as e:
            g["last_error"] = str(e)
            return

    g["last_decision"] = {
        "topic_idx": topic_idx,
        "vector": vector,
        "tier": tier,
        "allowed": decision.allowed,
        "reasons": decision.reasons,
        "risk_level": decision.risk_level,
        "source": decision.source,
    }

    if not decision.allowed:
        return

    with st.spinner("Generando plantilla..."):
        try:
            user_msg = template_generator.build_user_message(
                topic=topic, vector=vector, difficulty_tier=tier, alcance=alcance
            )
            resp = llm.call(
                system=template_generator.SYSTEM,
                user_message=user_msg,
                max_tokens=4000,
                output_schema=template_generator.SCHEMA,
            )
            llm.log_generation(
                operator_hash=state.operator_hash(),
                section="generacion.template",
                config={
                    "topic_title_chars": len(topic["title"]),
                    "vector": vector,
                    "difficulty_tier": tier,
                    "risk_level": decision.risk_level,
                },
                usage=resp,
            )
            parsed = resp.parsed or {}
        except llm.LLMError as e:
            g["last_error"] = str(e)
            return

    if parsed.get("refused"):
        g["last_decision"] = {
            **(g["last_decision"] or {}),
            "allowed": False,
            "reasons": [
                "El generador rechazó la plantilla: "
                + (parsed.get("refusal_reason") or "razón no especificada")
            ],
            "source": "generator",
        }
        return

    template = parsed.get("template")
    if not template:
        g["last_error"] = "El generador no devolvió una plantilla. Reintentá."
        return

    g["templates"].append({
        "id": f"tpl_{len(g['templates']) + 1:03d}",
        "topic_idx": topic_idx,
        "topic_title": topic["title"],
        "vector": template["vector"],
        "difficulty_tier": tier,
        "risk_level": decision.risk_level,
        "subject": template.get("subject"),
        "body": template["body"],
        "sender_display_name": template["sender_display_name"],
        "sender_local_part": template.get("sender_local_part"),
        "sender_domain": alcance["sandbox_domain"],
        "detectable_indicators": template["detectable_indicators"],
        "landing_description": template["landing_description"],
        "training_objective": template["training_objective"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


def _render_decision_banner() -> None:
    g = _ensure_state()
    err = g.get("last_error")
    if err:
        st.error(err)
    decision = g.get("last_decision")
    if not decision:
        return
    if decision["allowed"]:
        if decision["risk_level"] in {"medio", "alto"}:
            st.warning(
                f"Plantilla generada. Riesgo: **{decision['risk_level']}**. "
                "Revisá la salida antes de exportarla."
            )
        else:
            st.success("Plantilla generada correctamente.")
    else:
        st.error(
            f"**Generación bloqueada** (origen: {decision['source']})\n\n"
            + "\n".join(f"- {r}" for r in decision["reasons"])
            + "\n\nAjustá el tema, vector o dificultad y reintentá. Si creés "
            "que el bloqueo es injustificado, contactá al responsable interno."
        )


def _render_template(t: dict[str, Any]) -> None:
    badge = f"`{t['id']}` · {t['vector'].upper()} · Tier {t['difficulty_tier']}"
    if t["risk_level"] != "bajo":
        badge += f" · Riesgo {t['risk_level']}"
    with st.container(border=True):
        st.markdown(f"**{t['topic_title']}** — {badge}")

        sender = t["sender_display_name"]
        if t["vector"] == "email":
            sender = f"{t['sender_display_name']} <{t['sender_local_part']}@{t['sender_domain']}>"

        if t["vector"] == "email" and t.get("subject"):
            st.markdown(f"**Asunto:** {t['subject']}")
        st.markdown(f"**Remitente:** {sender}")
        st.markdown("**Cuerpo:**")
        st.code(t["body"], language="text")

        with st.expander("Indicadores detectables (para debrief)"):
            for ind in t["detectable_indicators"]:
                st.markdown(f"- {ind}")

        with st.expander("Landing educativa"):
            st.write(t["landing_description"])
            st.caption(f"Objetivo de capacitación: {t['training_objective']}")

        cols = st.columns([1, 5])
        with cols[0]:
            if st.button("Eliminar", key=f"del_{t['id']}"):
                g = _ensure_state()
                g["templates"] = [x for x in g["templates"] if x["id"] != t["id"]]
                st.rerun()


def render() -> None:
    plan = st.session_state.get("planificacion")
    alcance = st.session_state.get("alcance")
    if not plan or not plan.get("topics") or not alcance:
        st.warning("No hay temas seleccionados. Volvé a planificación.")
        if st.button("Volver"):
            state.goto("planificacion")
        return

    st.subheader("Generación de plantillas")
    g = _ensure_state()

    _render_decision_banner()

    st.markdown("### Temas en agenda")
    st.caption(
        "Para cada tema, configurá vector + dificultad y generá una o más plantillas. "
        "El safety filter corre antes de cada generación."
    )
    for i, topic in enumerate(plan["topics"]):
        _topic_card(i, topic, alcance)

    if g["templates"]:
        st.divider()
        st.markdown(f"### Plantillas generadas ({len(g['templates'])})")
        for t in g["templates"]:
            _render_template(t)

        st.divider()
        cols = st.columns([1, 5])
        with cols[0]:
            if st.button("Continuar a exportación", type="primary"):
                state.goto("exportacion")
