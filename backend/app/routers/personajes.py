"""Endpoints de personajes ficticios."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Arquetipo, NivelDificultad
from app.schemas.personaje import PersonajeCreate, PersonajeRead
from app.services.personajes_service import PersonajesService

router = APIRouter(prefix="/personajes", tags=["personajes"])


@router.get("", response_model=list[PersonajeRead])
def listar(
    arquetipo: Arquetipo | None = Query(None),
    nivel: NivelDificultad | None = Query(None),
    organizacion_id: UUID | None = Query(None),
    solo_semilla: bool = Query(False),
    db: Session = Depends(get_db),
):
    return PersonajesService.listar(db, arquetipo, nivel, organizacion_id, solo_semilla)


@router.get("/{personaje_id}", response_model=PersonajeRead)
def obtener(personaje_id: UUID, db: Session = Depends(get_db)):
    p = PersonajesService.obtener(db, personaje_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "personaje_no_encontrado")
    return p


@router.post("", response_model=PersonajeRead, status_code=status.HTTP_201_CREATED)
def crear(payload: PersonajeCreate, db: Session = Depends(get_db)):
    try:
        return PersonajesService.crear(db, payload)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
