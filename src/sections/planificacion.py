"""Sección 4: Planificación de campaña.

Stub para Fase 2. El asistente IA preguntará si el cliente tiene un plan
mensual con temáticas predefinidas, o si necesita propuestas basadas en
amenazas vigentes.
"""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.subheader("Planificación de campaña")
    st.info(
        "Fase 2 (próxima): asistente IA conversacional para levantar necesidades "
        "de contenido o proponer temáticas según amenazas vigentes."
    )
    st.caption(
        "Esta sección quedará disponible una vez completada la Fase 2 del proyecto. "
        "Por ahora podés revisar el alcance que cargaste:"
    )
    a = st.session_state.get("alcance") or {}
    st.json({k: (str(v) if hasattr(v, "isoformat") else v) for k, v in a.items()})
