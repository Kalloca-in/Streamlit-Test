"""Esquemas Pydantic para Día Triple, Acto e Indicador."""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import (
    CanalAtaque,
    GanchoPsicologico,
    NivelDificultad,
    Rol,
    TipoIndicador,
)


class IndicadorBase(BaseModel):
    tipo: TipoIndicador
    fragmento: str = Field(..., min_length=2, max_length=500)
    explicacion: str = Field(..., min_length=10)


class IndicadorRead(IndicadorBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class OpcionDecision(BaseModel):
    id: str = Field(..., pattern=r"^[a-d]$")
    texto: str
    consecuencia: str
    es_segura: bool


class ActoBase(BaseModel):
    orden: int = Field(..., ge=1, le=3)
    rol: Rol
    canal: CanalAtaque
    hora_dramatizada: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    remitente_aparente: str
    asunto: str | None = None
    cuerpo: str = Field(..., min_length=10)
    marca_ficticia_slug: str | None = None
    opciones_decision: list[OpcionDecision] = Field(..., min_length=3, max_length=4)
    indicadores: list[IndicadorBase] = Field(..., min_length=3, max_length=6)


class ActoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    orden: int
    rol: Rol
    canal: CanalAtaque
    hora_dramatizada: str
    remitente_aparente: str
    asunto: str | None
    cuerpo: str
    marca_ficticia_slug: str | None
    opciones_decision: list[OpcionDecision]
    indicadores: list[IndicadorRead]


class DiaTripleCreate(BaseModel):
    personaje_id: UUID
    titulo: str
    gancho_psicologico_raiz: GanchoPsicologico
    nivel_dificultad: NivelDificultad
    nota_revelacion: str = Field(..., min_length=20)
    actos: list[ActoBase] = Field(..., min_length=3, max_length=3)

    @model_validator(mode="after")
    def _validar_tres_roles_distintos(self) -> "DiaTripleCreate":
        roles = {a.rol for a in self.actos}
        if roles != {Rol.CIUDADANO, Rol.COLABORADOR, Rol.CLIENTE}:
            raise ValueError(
                "Un Día Triple debe contener exactamente un Acto por cada rol "
                "(ciudadano, colaborador, cliente)."
            )
        return self


class DiaTripleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    personaje_id: UUID
    titulo: str
    gancho_psicologico_raiz: GanchoPsicologico
    nivel_dificultad: NivelDificultad
    nota_revelacion: str
    actos: list[ActoRead]
