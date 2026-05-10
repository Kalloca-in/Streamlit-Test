"""Sección 2: Acuerdo de uso responsable.

Gate obligatorio antes de cualquier funcionalidad. El operador declara
explícitamente las condiciones bajo las cuales puede usar la plataforma.

El gate es auto-atestación: no verifica el contrato. Está pensado para forzar
una pausa consciente, dejar registro de aceptación y rechazar accesos casuales.
La validación real del scope vive en el contrato firmado entre el operador y su
cliente, y debe estar aprobada antes de tipear el primer caracter aquí.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from src import state

DECLARACIONES = [
    "Cuento con autorización contractual escrita y vigente del cliente "
    "para ejecutar simulaciones de phishing con fines de concientización.",
    "Las simulaciones se dirigirán únicamente a colaboradores de la organización "
    "cliente, en su rol laboral, dentro del perímetro corporativo autorizado. "
    "No se atacarán contextos personales (familiares, banca personal, hijos, salud).",
    "Los dominios remitentes y la infraestructura de envío serán dominios "
    "controlados por el cliente o por mí en su representación. No suplantaré "
    "marcas, instituciones, bancos ni terceros sin su consentimiento explícito.",
    "Entiendo que esta plataforma NO envía correos ni mensajes. Solo prepara "
    "contenido para que sea enviado mediante la infraestructura autorizada del "
    "cliente. Soy responsable del envío y del debrief educativo posterior.",
]


def render() -> None:
    op = st.session_state.get("operator")
    if not op:
        state.goto("login")
        return

    st.subheader("Acuerdo de uso responsable")
    st.caption(
        f"Operador: **{op['nombre']}** · Cliente declarado: **{op['cliente']}** · "
        f"Folio: `{op['folio']}`"
    )

    st.markdown(
        "Antes de continuar, confirmá cada una de las siguientes declaraciones. "
        "El uso no autorizado de esta plataforma contra terceros es ilegal."
    )

    checks: list[bool] = []
    for i, texto in enumerate(DECLARACIONES, start=1):
        checked = st.checkbox(f"**{i}.** {texto}", key=f"acuerdo_{i}")
        checks.append(checked)

    todos_marcados = all(checks)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(
            "Aceptar y continuar",
            type="primary",
            disabled=not todos_marcados,
        ):
            st.session_state.acuerdo = {
                "accepted_at": datetime.now(timezone.utc).isoformat(),
                "declaraciones": DECLARACIONES,
            }
            state.goto("alcance")
    with col2:
        if not todos_marcados:
            st.caption("Marcá las cuatro declaraciones para habilitar el botón.")
