"""Helpers para session_state.

La app es una máquina de estados con secciones. session_state guarda:
- section: cuál sección está activa
- operator: dict con identidad del operador (post-login)
- acuerdo: dict con timestamp y declaraciones aceptadas
- alcance: dict con la declaración de alcance corporativo
- planificacion: dict con modo (plan|proposals) y lista de topics
- generacion: dict con templates generadas y última decisión del safety filter
"""

from __future__ import annotations

import hashlib
from typing import Any

import streamlit as st

SECTIONS = [
    "login",
    "acuerdo",
    "alcance",
    "planificacion",
    "generacion",
    "exportacion",
]


def init() -> None:
    if "section" not in st.session_state:
        st.session_state.section = "login"
    for key in (
        "operator",
        "acuerdo",
        "alcance",
        "planificacion",
        "generacion",
    ):
        st.session_state.setdefault(key, None)


def goto(section: str) -> None:
    if section not in SECTIONS:
        raise ValueError(f"Sección desconocida: {section}")
    st.session_state.section = section
    st.rerun()


def operator_hash() -> str:
    """Hash estable del operador para logging sin exponer identidad."""
    op = st.session_state.get("operator") or {}
    seed = f"{op.get('nombre', '')}|{op.get('cliente', '')}".encode()
    return hashlib.sha256(seed).hexdigest()[:16]


def reset() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init()
    st.rerun()
