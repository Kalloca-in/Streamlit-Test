"""Endpoints mínimos de creación de usuarios y organizaciones (sin auth)."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario

router = APIRouter(tags=["usuarios"])


class OrganizacionIn(BaseModel):
    nombre: str
    slug: str
    sector: str | None = None


class OrganizacionOut(OrganizacionIn):
    id: UUID

    class Config:
        from_attributes = True


@router.post("/organizaciones", response_model=OrganizacionOut, status_code=status.HTTP_201_CREATED)
def crear_organizacion(payload: OrganizacionIn, db: Session = Depends(get_db)):
    if db.execute(select(Organizacion).where(Organizacion.slug == payload.slug)).scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "slug_organizacion_duplicado")
    o = Organizacion(nombre=payload.nombre, slug=payload.slug, sector=payload.sector)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


class UsuarioIn(BaseModel):
    organizacion_id: UUID
    identificador_externo: str
    area: str | None = None
    email: str | None = None


class UsuarioOut(UsuarioIn):
    id: UUID

    class Config:
        from_attributes = True


@router.post("/usuarios", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UsuarioIn, db: Session = Depends(get_db)):
    u = Usuario(
        organizacion_id=payload.organizacion_id,
        identificador_externo=payload.identificador_externo,
        area=payload.area,
        email=payload.email,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
