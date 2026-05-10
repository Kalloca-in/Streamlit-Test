"""
Sesión de aprendizaje + decisiones del usuario + reflexión personal.

PRIVACIDAD:
- `Reflexion` es estrictamente privada por usuario. Solo se expone agregada
  con n >= MIN_AGGREGATE_N.
- No se persiste OSINT del usuario real. Las respuestas son sobre el
  personaje y sobre la propia experiencia, no datos personales explotables.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import EstadoSesion, Rol
from app.models._mixins import Timestamped, UUIDPrimaryKey


class Sesion(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "sesiones"

    usuario_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    personaje_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("personajes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    dia_triple_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("dias_triples.id", ondelete="RESTRICT"),
        nullable=False,
    )
    estado: Mapped[EstadoSesion] = mapped_column(String(30), nullable=False, default=EstadoSesion.INICIADA)
    iniciada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    decisiones: Mapped[list["Decision"]] = relationship(
        "Decision",
        back_populates="sesion",
        cascade="all, delete-orphan",
    )
    reflexion: Mapped["Reflexion | None"] = relationship(
        "Reflexion",
        back_populates="sesion",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Decision(UUIDPrimaryKey, Timestamped, Base):
    """Decisión del usuario en un Acto durante el Día Triple."""

    __tablename__ = "decisiones"

    sesion_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("sesiones.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    acto_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("actos.id", ondelete="CASCADE"),
        nullable=False,
    )
    rol: Mapped[Rol] = mapped_column(String(20), nullable=False)
    opcion_elegida: Mapped[str] = mapped_column(String(20), nullable=False)
    fue_segura: Mapped[bool] = mapped_column(nullable=False)
    # Indicadores que el usuario marcó (si la UI lo permite). Lista de UUIDs.
    indicadores_detectados: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    sesion: Mapped["Sesion"] = relationship("Sesion", back_populates="decisiones")


class Reflexion(UUIDPrimaryKey, Timestamped, Base):
    """
    Auto-evaluación reflexiva (Mi Reflejo). PRIVADA por usuario.
    No se expone individualmente al empleador.
    """

    __tablename__ = "reflexiones"

    sesion_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("sesiones.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    rol_mas_vulnerable: Mapped[Rol | None] = mapped_column(String(20))
    eco_personal: Mapped[str | None] = mapped_column(Text)
    cambio_propuesto: Mapped[str | None] = mapped_column(Text)
    nivel_confianza: Mapped[int | None] = mapped_column(Integer)  # 1-5

    sesion: Mapped["Sesion"] = relationship("Sesion", back_populates="reflexion")
