"""
Organización cliente. Tenant lógico que agrupa facilitadores, usuarios,
personajes propios y reportes agregados.
"""
from sqlalchemy import String  # noqa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import Timestamped, UUIDPrimaryKey


class Organizacion(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "organizaciones"

    nombre: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    sector: Mapped[str | None] = mapped_column(String(80))
