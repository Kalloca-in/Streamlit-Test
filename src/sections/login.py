"""Sección 1: Login del operador.

Auth local básica: contraseña compartida en .env más identificación del operador
y referencia al engagement contractual. La contraseña no autentica una identidad —
solo acota el acceso a operadores autorizados de la organización que opera la
plataforma. La identidad declarada va al log de auditoría.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import streamlit as st

from src import state


def render() -> None:
    st.subheader("Acceso de operador")
    st.caption(
        "Esta plataforma está diseñada para uso interno de equipos de seguridad y proveedores "
        "de servicios de awareness con autorización contractual. El acceso queda registrado."
    )

    expected = os.environ.get("OPERATOR_PASSWORD", "")
    if not expected:
        st.error(
            "OPERATOR_PASSWORD no está configurado en el entorno. "
            "Configurá la variable en .env antes de usar la plataforma."
        )
        return

    with st.form("login_form", clear_on_submit=False):
        nombre = st.text_input(
            "Nombre del operador",
            help="Usado para registro de auditoría. No se almacena fuera de logs locales.",
        )
        cliente = st.text_input(
            "Cliente / organización del engagement",
            help="Razón social del cliente para el cual ejecutarás la campaña.",
        )
        folio = st.text_input(
            "Referencia contractual / N° de engagement",
            help="Identificador interno del contrato o ticket que autoriza esta operación.",
        )
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar", type="primary")

    if not submitted:
        return

    missing = [
        label
        for label, value in [
            ("Nombre", nombre),
            ("Cliente", cliente),
            ("Referencia contractual", folio),
            ("Contraseña", password),
        ]
        if not value.strip()
    ]
    if missing:
        st.error("Faltan campos: " + ", ".join(missing))
        return

    if password != expected:
        st.error("Contraseña incorrecta.")
        return

    st.session_state.operator = {
        "nombre": nombre.strip(),
        "cliente": cliente.strip(),
        "folio": folio.strip(),
        "login_at": datetime.now(timezone.utc).isoformat(),
    }
    state.goto("acuerdo")
