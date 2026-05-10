"""Sección 4: Planificación de campaña.

Dos modos:
- "tengo plan": el operador pega el plan mensual del cliente, el asistente
  IA lo estructura en una lista de temas.
- "necesito propuestas": el asistente IA propone 6-8 temas según alcance
  y amenazas vigentes.

En ambos casos el output es una lista de temas que pasa a generación.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src import llm, state
from src.prompts import campaign_planner, topic_proposer


def _render_topics_table(topics: list[dict[str, Any]]) -> None:
    for i, t in enumerate(topics, start=1):
        with st.container(border=True):
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(f"**{i}. {t['title']}**")
                st.caption(t["threat_summary"])
                meta = f"Audiencia: {t['target_audience']} · Tier sugerido: {t['suggested_difficulty_tier']}"
                if t.get("rationale"):
                    meta += f" · {t['rationale']}"
                st.caption(meta)
            with cols[1]:
                if st.button("Quitar", key=f"rm_topic_{i}"):
                    plan = st.session_state.planificacion or {}
                    plan["topics"] = [
                        x for x in plan.get("topics", []) if x is not t
                    ]
                    st.session_state.planificacion = plan
                    st.rerun()


def _mode_picker() -> None:
    st.markdown(
        "El asistente puede trabajar de dos formas. ¿Cómo querés arrancar?"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Tengo plan del cliente",
            use_container_width=True,
            help="Pegás el plan mensual y el asistente lo estructura en temas.",
        ):
            st.session_state.planificacion = {"mode": "plan", "topics": []}
            st.rerun()
    with col2:
        if st.button(
            "Necesito propuestas",
            type="primary",
            use_container_width=True,
            help="El asistente propone 6-8 temas según el alcance y amenazas vigentes.",
        ):
            st.session_state.planificacion = {"mode": "proposals", "topics": []}
            st.rerun()


def _plan_flow(alcance: dict[str, Any]) -> None:
    plan = st.session_state.planificacion
    st.markdown(
        "**Modo:** estructurar plan del cliente. "
        "Pegá el plan mensual tal como lo recibiste — bullets, párrafos o tabla."
    )

    plan_text = st.text_area(
        "Plan mensual del cliente",
        value=plan.get("raw_plan", ""),
        height=200,
        placeholder=(
            "Ej:\n"
            "- Abril: phishing relacionado con cierre fiscal interno, dirigido a Finanzas\n"
            "- Abril: simulación de helpdesk de IT solicitando reset de MFA\n"
            "- Mayo: ..."
        ),
    )

    cols = st.columns([1, 1, 4])
    with cols[0]:
        run = st.button(
            "Estructurar plan",
            type="primary",
            disabled=not plan_text.strip(),
        )
    with cols[1]:
        if st.button("Cambiar modo"):
            st.session_state.planificacion = None
            st.rerun()

    if run:
        plan["raw_plan"] = plan_text
        with st.spinner("Estructurando plan..."):
            try:
                user_msg = campaign_planner.build_user_message(
                    plan_text=plan_text, alcance=alcance
                )
                resp = llm.call(
                    system=campaign_planner.SYSTEM,
                    user_message=user_msg,
                    max_tokens=4000,
                    output_schema=campaign_planner.SCHEMA,
                )
                llm.log_generation(
                    operator_hash=state.operator_hash(),
                    section="planificacion.plan",
                    config={"plan_chars": len(plan_text)},
                    usage=resp,
                )
                plan["topics"] = (resp.parsed or {}).get("topics", [])
                plan["warnings"] = (resp.parsed or {}).get("warnings", [])
                st.session_state.planificacion = plan
                st.rerun()
            except llm.LLMError as e:
                st.error(str(e))

    if plan.get("warnings"):
        st.warning(
            "Advertencias del asistente:\n\n"
            + "\n".join(f"- {w}" for w in plan["warnings"])
        )

    if plan.get("topics"):
        st.markdown(f"**Temas estructurados ({len(plan['topics'])}):**")
        _render_topics_table(plan["topics"])
        if st.button("Continuar a generación", type="primary"):
            state.goto("generacion")


def _proposals_flow(alcance: dict[str, Any]) -> None:
    plan = st.session_state.planificacion
    st.markdown(
        "**Modo:** propuestas asistidas. "
        "Opcionalmente indicá enfoques o restricciones, y generá 6-8 propuestas."
    )

    focos = st.text_area(
        "Enfoques o restricciones (opcional)",
        value=plan.get("focos", ""),
        height=100,
        placeholder=(
            "Ej: priorizar temas de credenciales y MFA porque están "
            "implementando passkeys este trimestre."
        ),
    )

    cols = st.columns([1, 1, 4])
    with cols[0]:
        run = st.button("Generar propuestas", type="primary")
    with cols[1]:
        if st.button("Cambiar modo"):
            st.session_state.planificacion = None
            st.rerun()

    if run:
        plan["focos"] = focos
        with st.spinner("Generando propuestas..."):
            try:
                user_msg = topic_proposer.build_user_message(
                    alcance=alcance, focos=focos
                )
                resp = llm.call(
                    system=topic_proposer.SYSTEM,
                    user_message=user_msg,
                    max_tokens=4000,
                    output_schema=topic_proposer.SCHEMA,
                )
                llm.log_generation(
                    operator_hash=state.operator_hash(),
                    section="planificacion.proposals",
                    config={"focos_chars": len(focos)},
                    usage=resp,
                )
                proposals = (resp.parsed or {}).get("topics", [])
                plan["proposals"] = proposals
                # No auto-seleccionamos: el operador elige cuáles ir a generación
                plan["selected"] = list(range(len(proposals)))
                st.session_state.planificacion = plan
                st.rerun()
            except llm.LLMError as e:
                st.error(str(e))

    proposals = plan.get("proposals", [])
    if proposals:
        st.markdown(f"**Propuestas ({len(proposals)}):**")
        st.caption("Marcá las que querés llevar a generación.")
        new_selected: list[int] = []
        for i, p in enumerate(proposals):
            with st.container(border=True):
                checked = st.checkbox(
                    f"**{p['title']}**",
                    value=(i in plan.get("selected", [])),
                    key=f"prop_{i}",
                )
                st.caption(p["threat_summary"])
                meta = (
                    f"Audiencia: {p['target_audience']} · "
                    f"Tier sugerido: {p['suggested_difficulty_tier']}"
                )
                if p.get("rationale"):
                    meta += f" · {p['rationale']}"
                st.caption(meta)
                if checked:
                    new_selected.append(i)
        plan["selected"] = new_selected
        st.session_state.planificacion = plan

        if st.button(
            "Confirmar selección y continuar",
            type="primary",
            disabled=not new_selected,
        ):
            plan["topics"] = [proposals[i] for i in new_selected]
            st.session_state.planificacion = plan
            state.goto("generacion")


def render() -> None:
    if not st.session_state.get("alcance"):
        state.goto("alcance")
        return

    st.subheader("Planificación de campaña")
    alcance = st.session_state.alcance

    plan = st.session_state.get("planificacion")
    if not plan:
        _mode_picker()
        return

    if plan["mode"] == "plan":
        _plan_flow(alcance)
    else:
        _proposals_flow(alcance)
