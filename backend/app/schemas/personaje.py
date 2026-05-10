"""Esquemas Pydantic para Personaje."""
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import Arquetipo, NivelDificultad


class VectorExposicion(BaseModel):
    """Superficies de ataque del personaje. Datos del personaje, NO del usuario real."""

    redes: list[str] = Field(default_factory=list)
    rutinas: list[str] = Field(default_factory=list)
    consumos: list[str] = Field(default_factory=list)


class PersonajeBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    edad: int = Field(..., ge=18, le=85)
    arquetipo: Arquetipo
    nivel_sugerido: NivelDificultad
    cargo_ficticio: str
    empresa_ficticia: str
    contexto_familiar: str
    habitos_consumo: str
    vector_exposicion: VectorExposicion
    avatar_url: str | None = None
    marcas_asociadas: list[str] = Field(default_factory=list)


class PersonajeCreate(PersonajeBase):
    organizacion_id: UUID | None = None
    es_semilla: bool = False


class PersonajeRead(PersonajeBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organizacion_id: UUID | None
    disclaimer_visible: bool
    es_semilla: bool


class PersonajeFiltro(BaseModel):
    """Parámetros de filtro para la galería de personajes."""

    arquetipo: Arquetipo | None = None
    nivel: NivelDificultad | None = None
    organizacion_id: UUID | None = None
