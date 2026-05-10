"""Endpoints de sesiones, decisiones y reflexiones."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sesion import (
    DecisionCreate,
    DecisionRead,
    ReflexionCreate,
    ReflexionRead,
    SesionCreate,
    SesionRead,
)
from app.services.sesion_service import SesionService

router = APIRouter(prefix="/sesiones", tags=["sesiones"])


@router.post("", response_model=SesionRead, status_code=status.HTTP_201_CREATED)
def crear(payload: SesionCreate, db: Session = Depends(get_db)):
    return SesionService.crear(db, payload)


@router.get("/{sesion_id}", response_model=SesionRead)
def obtener(sesion_id: UUID, db: Session = Depends(get_db)):
    s = SesionService.obtener(db, sesion_id)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "sesion_no_encontrada")
    return s


@router.post(
    "/{sesion_id}/decisiones",
    response_model=DecisionRead,
    status_code=status.HTTP_201_CREATED,
)
def registrar_decision(
    sesion_id: UUID, payload: DecisionCreate, db: Session = Depends(get_db)
):
    try:
        return SesionService.registrar_decision(db, sesion_id, payload)
    except LookupError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e


@router.post(
    "/{sesion_id}/reflexion",
    response_model=ReflexionRead,
    status_code=status.HTTP_201_CREATED,
)
def registrar_reflexion(
    sesion_id: UUID, payload: ReflexionCreate, db: Session = Depends(get_db)
):
    try:
        return SesionService.registrar_reflexion(db, sesion_id, payload)
    except LookupError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e


@router.get("/usuario/{usuario_id}/progreso")
def progreso_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    return SesionService.progreso_usuario(db, usuario_id)
