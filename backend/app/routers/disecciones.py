"""Endpoints de la Sala de Disección.

Devuelve los indicadores ya estructurados de un Acto. La generación con
LLM (prompt `disector`) se invoca solo si el Acto no tiene indicadores
persistidos —caso raro, porque dia_triple_writer ya los produce—.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dia_triple import Acto
from app.schemas.dia_triple import IndicadorRead

router = APIRouter(prefix="/disecciones", tags=["disecciones"])


@router.get("/acto/{acto_id}", response_model=list[IndicadorRead])
def diseccionar_acto(acto_id: UUID, db: Session = Depends(get_db)):
    acto = db.get(Acto, acto_id)
    if acto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "acto_no_encontrado")
    return list(acto.indicadores)
