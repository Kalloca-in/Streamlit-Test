"""Sección 6: Exportación de la campaña.

Genera un ZIP con manifest, GoPhish JSON, HTMLs por plantilla y PDF brief.
La descarga se entrega vía st.download_button. Nada se persiste server-side.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from src import state
from src.exporters import bundle


def render() -> None:
    g = st.session_state.get("generacion")
    op = st.session_state.get("operator")
    alcance = st.session_state.get("alcance")

    if not g or not g.get("templates"):
        st.warning("No hay plantillas generadas. Volvé a generación.")
        if st.button("Volver"):
            state.goto("generacion")
        return

    templates = g["templates"]
    st.subheader("Exportación de campaña")
    st.caption(
        f"Vas a empaquetar {len(templates)} plantilla(s) para entregar a la "
        "infraestructura de envío del cliente."
    )

    default_name = (
        f"awareness-{op['cliente'].lower().replace(' ', '-')}"
        f"-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    )
    campaign_name = st.text_input(
        "Nombre de la campaña",
        value=default_name,
        help="Se usa para el archivo descargado y el manifest interno.",
    )

    st.markdown("**Plantillas incluidas:**")
    for t in templates:
        risk_badge = "" if t["risk_level"] == "bajo" else f" · ⚠ Riesgo {t['risk_level']}"
        st.markdown(
            f"- `{t['id']}` · **{t['topic_title']}** · "
            f"{t['vector'].upper()} · Tier {t['difficulty_tier']}{risk_badge}"
        )

    st.divider()

    try:
        zip_bytes = bundle.build_zip(
            campaign_name=campaign_name,
            operator=op,
            alcance=alcance,
            templates=templates,
        )
    except Exception as e:
        st.error(f"Error al generar el paquete: {e}")
        return

    cols = st.columns([2, 2, 3])
    with cols[0]:
        st.download_button(
            "Descargar paquete (.zip)",
            data=zip_bytes,
            file_name=f"{campaign_name}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )
    with cols[1]:
        if st.button("Volver a generación", use_container_width=True):
            state.goto("generacion")
    with cols[2]:
        if st.button("Cerrar campaña y reiniciar", use_container_width=True):
            state.reset()

    st.caption(
        "El paquete se generó en memoria y nunca se almacenó en disco. "
        "Una vez descargado, asegurate de manejarlo según las políticas de "
        "datos del cliente."
    )
