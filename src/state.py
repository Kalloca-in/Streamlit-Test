"""Helpers para session_state.

La app es una máquina de estados con secciones. session_state guarda:
- section: cuál sección está activa
- operator: dict con identidad del operador (post-login)
- acuerdo: dict con timestamp y checks aceptados
- alcance: dict con la declaración de alcance corporativo
- planificacion, generacion, exportacion: pendientes para fases siguientes
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
    for key in ("operator", "acuerdo", "alcance", "planificacion", "generacion"):
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


def require(*sections_done: str) -> None:
    """Si alguna sección requerida no está completa, regresa a la primera faltante."""
    for s in sections_done:
        if not st.session_state.get(s):
            goto(s)


def reset() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init()


def snapshot() -> dict[str, Any]:
    """Snapshot de configuración actual (sin contenidos generados) para logging."""
    return {
        "operator_set": bool(st.session_state.get("operator")),
        "acuerdo_set": bool(st.session_state.get("acuerdo")),
        "alcance": _safe_alcance(),
    }


def _safe_alcance() -> dict[str, Any] | None:
    a = st.session_state.get("alcance")
    if not a:
        return None
    return {
        "sector": a.get("sector"),
        "tamano": a.get("tamano"),
        "departamentos_count": len(a.get("departamentos", [])),
        "topicos_excluidos_count": len(a.get("topicos_excluidos", [])),
    }
