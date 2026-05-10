"""
Punto de entrada FastAPI de CiberTeatro.

Compromisos codificados al startup:
- Carga el catálogo cerrado de marcas ficticias.
- (Bloque 2) Engancha el safety_filter al cliente Anthropic.
- Expone /health y /principios para visibilidad pública del compromiso.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.core.config import get_settings
from app.core.database import Base, engine

# Importar `app.models` registra todos los modelos en SQLAlchemy.
# El `noqa` evita que un linter lo elimine: el import tiene side-effect deliberado.
import app.models  # noqa: F401
from app.routers import (
    dias_triples,
    disecciones,
    health,
    marcas,
    personajes,
    reportes,
    sesiones,
    usuarios,
)
from app.services.anthropic_client import get_anthropic_service
from app.services.marcas_catalog import cargar_catalogo

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    log.info("Iniciando CiberTeatro v%s en entorno=%s", __version__, settings.environment)

    catalogo = cargar_catalogo()
    log.info("Catálogo de marcas ficticias cargado: %d entradas", len(catalogo))

    # En entornos de desarrollo / SQLite, crea las tablas si faltan.
    if settings.environment in {"development", "test"} or settings.database_url.startswith(
        "sqlite"
    ):
        Base.metadata.create_all(bind=engine)
        log.info("Tablas creadas/verificadas (modo dev).")

    # Hook para el safety_filter (lo provee el Bloque 2).
    # Si el módulo está disponible, se conecta al cliente Anthropic.
    try:
        from app.services.safety_filter import safety_pre_call_filter  # type: ignore

        get_anthropic_service().attach_safety_filter(safety_pre_call_filter)
        log.info("safety_filter conectado al cliente Anthropic.")
    except ImportError:
        log.warning(
            "safety_filter aún no implementado (esperado durante Bloque 1). "
            "El cliente Anthropic rechazará llamadas sin filtro en producción."
        )

    yield
    log.info("Shutting down CiberTeatro.")


app = FastAPI(
    title="CiberTeatro API",
    description=(
        "Plataforma de ilustración dramatizada para awareness en ciberseguridad. "
        "Triple-rol: ciudadano, colaborador, cliente. Personajes y marcas ficticias."
    ),
    version=__version__,
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(marcas.router)
app.include_router(personajes.router)
app.include_router(dias_triples.router)
app.include_router(sesiones.router)
app.include_router(disecciones.router)
app.include_router(usuarios.router)
app.include_router(reportes.router)
