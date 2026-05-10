"""Esquemas Pydantic para Sesión, Decisión y Reflexión."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import EstadoSesion, Rol


class SesionCreate(BaseModel):
    usuario_id: UUID
    personaje_id: UUID
    dia_triple_id: UUID


class SesionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    usuario_id: UUID
    personaje_id: UUID
    dia_triple_id: UUID
    estado: EstadoSesion
    iniciada_en: datetime | None
    completada_en: datetime | None


class DecisionCreate(BaseModel):
    acto_id: UUID
    rol: Rol
    opcion_elegida: str = Field(..., pattern=r"^[a-d]$")
    indicadores_detectados: list[UUID] = Field(default_factory=list)


class DecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    acto_id: UUID
    rol: Rol
    opcion_elegida: str
    fue_segura: bool
    indicadores_detectados: list[UUID]


class ReflexionCreate(BaseModel):
    rol_mas_vulnerable: Rol | None = None
    eco_personal: str | None = Field(default=None, max_length=2000)
    cambio_propuesto: str | None = Field(default=None, max_length=2000)
    nivel_confianza: int | None = Field(default=None, ge=1, le=5)


class ReflexionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sesion_id: UUID
    rol_mas_vulnerable: Rol | None
    eco_personal: str | None
    cambio_propuesto: str | None
    nivel_confianza: int | None
