"""Catálogo público de marcas ficticias (read-only)."""
from fastapi import APIRouter

from app.schemas.marca import MarcaFicticia
from app.services.marcas_catalog import cargar_catalogo

router = APIRouter(prefix="/marcas", tags=["marcas"])


@router.get("", response_model=list[MarcaFicticia])
def listar_marcas() -> list[MarcaFicticia]:
    return cargar_catalogo()
