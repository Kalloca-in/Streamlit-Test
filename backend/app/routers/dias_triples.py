"""Endpoints de Días Triples."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dia_triple import DiaTripleCreate, DiaTripleRead
from app.services.dia_triple_service import DiaTripleService
from app.services.safety_filter import SafetyViolation

router = APIRouter(prefix="/dias-triples", tags=["dias-triples"])


@router.get("/personaje/{personaje_id}", response_model=list[DiaTripleRead])
def listar_por_personaje(personaje_id: UUID, db: Session = Depends(get_db)):
    return DiaTripleService.listar_por_personaje(db, personaje_id)


@router.get("/{dia_triple_id}", response_model=DiaTripleRead)
def obtener(dia_triple_id: UUID, db: Session = Depends(get_db)):
    dt = DiaTripleService.obtener(db, dia_triple_id)
    if not dt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "dia_triple_no_encontrado")
    return dt


@router.post("", response_model=DiaTripleRead, status_code=status.HTTP_201_CREATED)
def crear(payload: DiaTripleCreate, db: Session = Depends(get_db)):
    try:
        return DiaTripleService.crear(db, payload)
    except SafetyViolation as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"motivo": e.motivo, "detalles": e.detalles},
        ) from e
