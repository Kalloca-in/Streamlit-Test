"""
Servicio de carga del catálogo cerrado de marcas ficticias.

El archivo `app/data/marcas_ficticias.json` es la fuente única de verdad.
El catálogo completo (>= 30 entradas) se entrega en el Bloque 2; este
módulo es la API estable de acceso desde el resto del backend.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas.marca import MarcaFicticia

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "marcas_ficticias.json"


class CatalogoMarcasError(RuntimeError):
    """Error al cargar el catálogo de marcas ficticias."""


@lru_cache
def cargar_catalogo() -> list[MarcaFicticia]:
    if not _DATA_PATH.exists():
        # En el bootstrap inicial el archivo puede no existir todavía.
        # El safety_filter del Bloque 2 trata el catálogo vacío como
        # "ninguna marca permitida" — falla cerrado, nunca abierto.
        return []
    try:
        data = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise CatalogoMarcasError(f"JSON inválido en {_DATA_PATH}: {e}") from e

    if not isinstance(data, list):
        raise CatalogoMarcasError("El catálogo debe ser una lista JSON.")

    return [MarcaFicticia.model_validate(item) for item in data]


def slugs_validos() -> set[str]:
    return {m.slug for m in cargar_catalogo()}


def nombres_validos_lower() -> set[str]:
    return {m.nombre.lower() for m in cargar_catalogo()}


def buscar_por_slug(slug: str) -> MarcaFicticia | None:
    for m in cargar_catalogo():
        if m.slug == slug:
            return m
    return None
