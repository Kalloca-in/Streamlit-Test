"""Esquema de marca ficticia. Cargado desde el catálogo cerrado."""
from pydantic import BaseModel, Field


class MarcaFicticia(BaseModel):
    """
    Entrada del catálogo cerrado de marcas ficticias.
    Defensa estructural contra el uso de marcas reales.
    """

    slug: str = Field(..., min_length=2, max_length=80)
    nombre: str
    sector: str
    dominio: str
    logo_placeholder: str
    descripcion: str
