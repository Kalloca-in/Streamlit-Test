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
from src.sections import acuerdo, alcance, login, planificacion

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
}


def header() -> None:
    st.title("Plataforma de Awareness")
    st.warning(
        "Herramienta para ejercicios de concientización autorizados. "
        "El uso no autorizado contra terceros es ilegal.",
        icon=None,
    )


def progress() -> None:
    """Barra de progreso entre secciones, solo informativa."""
    order = ["login", "acuerdo", "alcance", "planificacion"]
    current = st.session_state.get("section", "login")
    if current not in order:
        return
    idx = order.index(current)
    cols = st.columns(len(order))
    labels = ["Acceso", "Acuerdo", "Alcance", "Planificación"]
    for i, (col, label) in enumerate(zip(cols, labels)):
        with col:
            mark = "●" if i <= idx else "○"
            style = "**" if i == idx else ""
            col.markdown(f"<div style='text-align:center'>{style}{mark} {label}{style}</div>", unsafe_allow_html=True)


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
        st.markdown("### Esta plataforma")
        st.caption(
            "Prepara plantillas de phishing simulado para programas de "
            "awareness corporativo. **No envía mensajes.** No genera ataques "
            "personalizados contra individuos. No suplanta marcas reales."
        )


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
        st.caption("Fase 1: Acceso y alcance")


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


if __name__ == "__main__":
    main()
else:
    main()
