"""
Modelos de Día Triple.

Estructura: un DiaTriple agrupa exactamente tres Actos (uno por rol).
Los tres Actos comparten gancho_psicologico_raiz; cambia el disfraz, no
la trampa. Cada Acto tiene 3-6 Indicadores detectables.
"""
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, GUID, JSONType
from app.core.enums import (
    CanalAtaque,
    GanchoPsicologico,
    NivelDificultad,
    Rol,
    TipoIndicador,
)
from app.models._mixins import Timestamped, UUIDPrimaryKey


class DiaTriple(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "dias_triples"
    __table_args__ = (
        CheckConstraint(
            "nivel_dificultad >= 1 AND nivel_dificultad <= 3",
            name="ck_dia_triple_dificultad_techo",
        ),
    )

    personaje_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("personajes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    gancho_psicologico_raiz: Mapped[GanchoPsicologico] = mapped_column(
        String(40), nullable=False, index=True
    )
    nivel_dificultad: Mapped[NivelDificultad] = mapped_column(Integer, nullable=False)

    # Nota didáctica que se muestra en la "revelación post-día".
    nota_revelacion: Mapped[str] = mapped_column(Text, nullable=False)

    actos: Mapped[list["Acto"]] = relationship(
        "Acto",
        back_populates="dia_triple",
        cascade="all, delete-orphan",
        order_by="Acto.orden",
    )


class Acto(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "actos"
    __table_args__ = (
        UniqueConstraint("dia_triple_id", "rol", name="uq_acto_dia_rol"),
        CheckConstraint("orden BETWEEN 1 AND 3", name="ck_acto_orden"),
    )

    dia_triple_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("dias_triples.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    rol: Mapped[Rol] = mapped_column(String(20), nullable=False)
    canal: Mapped[CanalAtaque] = mapped_column(String(30), nullable=False)
    hora_dramatizada: Mapped[str] = mapped_column(String(10), nullable=False)  # "07:30"

    remitente_aparente: Mapped[str] = mapped_column(String(200), nullable=False)
    asunto: Mapped[str | None] = mapped_column(String(255))
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)

    # Slug de marca ficticia usada (si aplica). Se valida contra el catálogo.
    marca_ficticia_slug: Mapped[str | None] = mapped_column(String(80))

    # Opciones de decisión que se ofrecen al usuario, formato:
    #   [{"id": "a", "texto": "...", "consecuencia": "...", "es_segura": bool}, ...]
    opciones_decision: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)

    dia_triple: Mapped["DiaTriple"] = relationship("DiaTriple", back_populates="actos")
    indicadores: Mapped[list["Indicador"]] = relationship(
        "Indicador",
        back_populates="acto",
        cascade="all, delete-orphan",
    )


class Indicador(UUIDPrimaryKey, Timestamped, Base):
    """Indicador detectable dentro de un Acto. Entre 3 y 6 por Acto."""

    __tablename__ = "indicadores"

    acto_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("actos.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    tipo: Mapped[TipoIndicador] = mapped_column(String(50), nullable=False)
    # Texto literal del mensaje que debe resaltarse.
    fragmento: Mapped[str] = mapped_column(String(500), nullable=False)
    # Explicación didáctica visible en la Sala de Disección.
    explicacion: Mapped[str] = mapped_column(Text, nullable=False)

    acto: Mapped["Acto"] = relationship("Acto", back_populates="indicadores")
