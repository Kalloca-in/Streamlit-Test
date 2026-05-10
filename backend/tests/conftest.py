"""
Configuración compartida de tests.

- Limpia el caché del catálogo entre tests para que los que crean
  catálogos temporales no se filtren a otros tests.
- Por defecto silencia el persistidor de SafetyLog (no hay DB en tests
  unitarios).
"""
from __future__ import annotations

import os

# Variables para que la app importe sin errores en tests.
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test"
)

import pytest

from app.services import marcas_catalog, safety_filter


@pytest.fixture(autouse=True)
def _silenciar_safety_log(monkeypatch):
    """En unitarios no hay DB. Reemplaza el persistidor por no-op."""
    monkeypatch.setattr(safety_filter, "_persistir_log", lambda **kwargs: None)


@pytest.fixture(autouse=True)
def _reset_catalogo_cache():
    marcas_catalog.cargar_catalogo.cache_clear()
    yield
    marcas_catalog.cargar_catalogo.cache_clear()
