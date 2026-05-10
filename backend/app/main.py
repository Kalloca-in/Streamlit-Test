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

# Importar `app.models` registra todos los modelos en SQLAlchemy.
# El `noqa` evita que un linter lo elimine: el import tiene side-effect deliberado.
import app.models  # noqa: F401
from app.routers import health
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
