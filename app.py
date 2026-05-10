"""Plataforma de Awareness — Generador de Campañas de Phishing Simuladas.

Aplicación Streamlit que ayuda a equipos de seguridad a preparar campañas
de awareness con plantillas asistidas por IA. La plataforma NO envía nada.

Diseño: máquina de estados por sección. Cada sección vive en src/sections/.
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from src import state
from src.sections import (
    acuerdo,
    alcance,
    exportacion,
    generacion,
    login,
    planificacion,
)

load_dotenv()

st.set_page_config(
    page_title="Plataforma de Awareness",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

SECTION_RENDERERS = {
    "login": login.render,
    "acuerdo": acuerdo.render,
    "alcance": alcance.render,
    "planificacion": planificacion.render,
    "generacion": generacion.render,
    "exportacion": exportacion.render,
}

PROGRESS_ORDER = ["login", "acuerdo", "alcance", "planificacion", "generacion", "exportacion"]
PROGRESS_LABELS = ["Acceso", "Acuerdo", "Alcance", "Planificación", "Generación", "Exportación"]


def header() -> None:
    st.title("Plataforma de Awareness")
    st.warning(
        "Herramienta para ejercicios de concientización autorizados. "
        "El uso no autorizado contra terceros es ilegal.",
        icon=None,
    )


def progress() -> None:
    current = st.session_state.get("section", "login")
    if current not in PROGRESS_ORDER:
        return
    idx = PROGRESS_ORDER.index(current)
    cols = st.columns(len(PROGRESS_ORDER))
    for i, (col, label) in enumerate(zip(cols, PROGRESS_LABELS)):
        with col:
            mark = "●" if i <= idx else "○"
            style = "**" if i == idx else ""
            col.markdown(
                f"<div style='text-align:center;font-size:13px'>"
                f"{style}{mark} {label}{style}</div>",
                unsafe_allow_html=True,
            )


def sidebar() -> None:
    op = st.session_state.get("operator")
    with st.sidebar:
        st.markdown("### Sesión")
        if op:
            st.caption(f"**{op['nombre']}**")
            st.caption(f"Cliente: {op['cliente']}")
            st.caption(f"Folio: `{op['folio']}`")
            if st.button("Cerrar sesión", use_container_width=True):
                state.reset()
        else:
            st.caption("Sin sesión activa")

        st.divider()

        if op:
            st.markdown("### Navegación")
            for sec, label in zip(PROGRESS_ORDER[1:], PROGRESS_LABELS[1:]):
                disabled = not _can_visit(sec)
                if st.button(label, key=f"nav_{sec}", disabled=disabled, use_container_width=True):
                    state.goto(sec)
            st.divider()

        st.markdown("### Esta plataforma")
        st.caption(
            "Prepara plantillas de phishing simulado para programas de "
            "awareness corporativo. **No envía mensajes.** No genera ataques "
            "personalizados contra individuos. No suplanta marcas reales."
        )


def _can_visit(section: str) -> bool:
    """Permite navegar solo a secciones cuyas dependencias están completas."""
    deps = {
        "acuerdo": ["operator"],
        "alcance": ["operator", "acuerdo"],
        "planificacion": ["operator", "acuerdo", "alcance"],
        "generacion": ["operator", "acuerdo", "alcance"],
        "exportacion": ["operator", "acuerdo", "alcance"],
    }
    needed = deps.get(section, [])
    if section in {"generacion", "exportacion"}:
        plan = st.session_state.get("planificacion")
        if not plan or not plan.get("topics"):
            return False
    if section == "exportacion":
        gen = st.session_state.get("generacion")
        if not gen or not gen.get("templates"):
            return False
    return all(st.session_state.get(k) for k in needed)


def footer() -> None:
    version = os.environ.get("APP_VERSION", "0.0.0")
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(
            f"Versión {version} · Para reportar uso indebido de esta plataforma, "
            "contactá al responsable interno de seguridad de tu organización."
        )
    with col2:
        st.caption("Plataforma de Awareness")


def main() -> None:
    state.init()
    header()
    sidebar()
    if st.session_state.get("operator"):
        progress()
    st.divider()

    section = st.session_state.get("section", "login")
    renderer = SECTION_RENDERERS.get(section)
    if renderer is None:
        st.error(f"Sección desconocida: {section}")
        if st.button("Volver al inicio"):
            state.reset()
    else:
        renderer()

    footer()


main()
