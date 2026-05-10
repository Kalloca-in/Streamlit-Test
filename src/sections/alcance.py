"""Sección 3: Alcance corporativo del engagement.

El operador declara explícitamente:
- A quién va dirigido (cliente, sector, tamaño)
- Cuál es el dominio sandbox que controla y aparecerá como remitente
- Qué departamentos están en scope
- Qué temáticas quedan vetadas (con un piso por defecto que no se puede desactivar)
- La vigencia del engagement

Estos campos limitan el espacio de generación en pantallas posteriores.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

import streamlit as st

from src import state

SECTORES = [
    "Banca / Finanzas",
    "Salud",
    "Retail / Consumo",
    "Tecnología",
    "Energía / Utilities",
    "Gobierno / Sector público",
    "Educación",
    "Manufactura",
    "Servicios profesionales",
    "Otro",
]

TAMANOS = [
    "Menos de 50 colaboradores",
    "50–250",
    "250–1.000",
    "1.000–5.000",
    "Más de 5.000",
]

# Temáticas vetadas por defecto. El operador puede agregar más, no quitar.
TOPICOS_VETADOS_DEFAULT = [
    "Salud o enfermedad de familiares",
    "Custodia o situación legal de hijos",
    "Deudas personales o juicios civiles",
    "Denuncias judiciales o policiales falsas",
    "Fallecimientos o emergencias familiares",
    "Suplantación de instituciones públicas (fiscalía, policía, militares)",
]

DOMAIN_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$")


def render() -> None:
    if not st.session_state.get("acuerdo"):
        state.goto("acuerdo")
        return

    st.subheader("Alcance del engagement")
    st.caption(
        "Definí los límites del ejercicio. La plataforma usará esto para acotar "
        "qué plantillas puede proponer y cuáles bloquea automáticamente."
    )

    prev = st.session_state.get("alcance") or {}

    with st.form("alcance_form"):
        col1, col2 = st.columns(2)
        with col1:
            sector = st.selectbox(
                "Sector del cliente",
                SECTORES,
                index=SECTORES.index(prev["sector"]) if prev.get("sector") in SECTORES else 0,
            )
            tamano = st.selectbox(
                "Tamaño aproximado",
                TAMANOS,
                index=TAMANOS.index(prev["tamano"]) if prev.get("tamano") in TAMANOS else 0,
            )
        with col2:
            sandbox_domain = st.text_input(
                "Dominio sandbox controlado",
                value=prev.get("sandbox_domain", ""),
                help=(
                    "El dominio desde el cual saldrán los correos simulados, "
                    "controlado por vos o el cliente. Ej: awareness-acme.com"
                ),
                placeholder="awareness-acme.com",
            )
            landing_base = st.text_input(
                "URL base de landing educativa (opcional)",
                value=prev.get("landing_base", ""),
                help=(
                    "Donde redirigirán los enlaces de las simulaciones para mostrar "
                    "el debrief al colaborador que hizo clic."
                ),
                placeholder="https://aprende.awareness-acme.com",
            )

        col3, col4 = st.columns(2)
        with col3:
            inicio = st.date_input(
                "Inicio de vigencia del engagement",
                value=prev.get("inicio", date.today()),
            )
        with col4:
            fin = st.date_input(
                "Fin de vigencia del engagement",
                value=prev.get("fin", date.today()),
            )

        departamentos = st.text_area(
            "Departamentos / áreas en scope",
            value="\n".join(prev.get("departamentos", [])),
            help="Uno por línea. Ej: Finanzas, RRHH, Operaciones, IT",
            height=120,
        )

        st.markdown("**Temáticas vetadas (no se pueden desactivar)**")
        for t in TOPICOS_VETADOS_DEFAULT:
            st.markdown(f"- {t}")

        topicos_extra = st.text_area(
            "Agregar temáticas vetadas adicionales (opcional)",
            value="\n".join(
                t for t in prev.get("topicos_excluidos", [])
                if t not in TOPICOS_VETADOS_DEFAULT
            ),
            help="Una por línea. Útil para temas sensibles propios del cliente.",
            height=80,
        )

        submitted = st.form_submit_button("Guardar alcance y continuar", type="primary")

    if not submitted:
        return

    errores: list[str] = []
    if not sandbox_domain.strip():
        errores.append("Dominio sandbox es requerido.")
    elif not DOMAIN_RE.match(sandbox_domain.strip()):
        errores.append("El dominio sandbox no parece válido.")

    if landing_base.strip() and not landing_base.startswith(("http://", "https://")):
        errores.append("La URL de landing debe empezar con http:// o https://")

    deps = [d.strip() for d in departamentos.splitlines() if d.strip()]
    if not deps:
        errores.append("Declarar al menos un departamento en scope.")

    if fin < inicio:
        errores.append("La fecha de fin no puede ser anterior al inicio.")

    if errores:
        for e in errores:
            st.error(e)
        return

    extras = [t.strip() for t in topicos_extra.splitlines() if t.strip()]
    topicos_excluidos = list(dict.fromkeys(TOPICOS_VETADOS_DEFAULT + extras))

    st.session_state.alcance = {
        "sector": sector,
        "tamano": tamano,
        "sandbox_domain": sandbox_domain.strip(),
        "landing_base": landing_base.strip() or None,
        "inicio": inicio,
        "fin": fin,
        "departamentos": deps,
        "topicos_excluidos": topicos_excluidos,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    state.goto("planificacion")
