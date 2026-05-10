"""Endpoints de salud y metadatos públicos no sensibles."""
from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@router.get("/principios")
def principios() -> dict:
    """
    Expone los principios no negociables como dato público de la API.
    El frontend los puede mostrar como compromiso visible al usuario.
    """
    settings = get_settings()
    return {
        "principios": [
            "Nunca se ataca al usuario real.",
            "Nunca se solicita ni procesa OSINT del usuario real.",
            "Marcas e instituciones son siempre ficticias, de un catálogo cerrado.",
            "El propósito es detección post-hoc, no captura.",
            "La dificultad escala pedagógicamente, nunca a indistinguible.",
        ],
        "max_dificultad": settings.max_difficulty,
        "min_n_para_reporte_agregado": settings.min_aggregate_n,
    }
