"""
Personajes ficticios protagonistas.

Todo personaje es DECLARADAMENTE FICTICIO. El campo `disclaimer_visible`
es siempre True y se renderiza en el frontend en cada pantalla del
personaje. Las marcas referenciadas en su contexto provienen únicamente
del catálogo cerrado en `data/marcas_ficticias.json`.
"""
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, GUID, JSONType
from app.core.enums import Arquetipo, NivelDificultad
from app.models._mixins import Timestamped, UUIDPrimaryKey


class Personaje(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "personajes"

    # Si organizacion_id es NULL, el personaje pertenece al catálogo global semilla.
    organizacion_id: Mapped[UUID | None] = mapped_column(
        GUID(),
        ForeignKey("organizaciones.id", ondelete="SET NULL"),
        index=True,
    )

    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    arquetipo: Mapped[Arquetipo] = mapped_column(String(40), nullable=False, index=True)
    nivel_sugerido: Mapped[NivelDificultad] = mapped_column(Integer, nullable=False)

    # Contexto narrativo
    cargo_ficticio: Mapped[str] = mapped_column(String(160), nullable=False)
    empresa_ficticia: Mapped[str] = mapped_column(String(160), nullable=False)
    contexto_familiar: Mapped[str] = mapped_column(Text, nullable=False)
    habitos_consumo: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector de exposición: lista estructurada de superficies de ataque.
    # JSONB con la forma {"redes": [...], "rutinas": [...], "consumos": [...]}
    vector_exposicion: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    # URL de avatar ilustrado (no fotorrealista). Generado o seleccionado de set fijo.
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    # Bandera siempre True. Defensa en profundidad: el frontend la lee y muestra disclaimer.
    disclaimer_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Marcas ficticias asociadas a este personaje (banco habitual, retailer, etc).
    # Lista de slugs que existen en `data/marcas_ficticias.json`.
    marcas_asociadas: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)

    es_semilla: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
