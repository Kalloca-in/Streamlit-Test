"""
Usuarios y facilitadores.

NOTA DE PRIVACIDAD: el `email` del usuario es opcional. La plataforma
puede operar con identificadores anónimos por sesión cuando el cliente
así lo configura. NO se solicita ni almacena ningún OSINT del usuario.
"""
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, GUID
from app.models._mixins import Timestamped, UUIDPrimaryKey


class Usuario(UUIDPrimaryKey, Timestamped, Base):
    """
    Colaborador-aprendiz. NUNCA se ataca directamente. Sus datos son
    estrictamente: identificador, organización, progreso, reflexiones.
    """

    __tablename__ = "usuarios"

    organizacion_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("organizaciones.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Identificador externo. Puede ser un alias anónimo emitido por el cliente.
    identificador_externo: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    # Email opcional, solo si la organización lo permite y el usuario consiente.
    email: Mapped[str | None] = mapped_column(String(160), unique=True)
    # Etiqueta de área/equipo dentro de la organización (no PII granular).
    area: Mapped[str | None] = mapped_column(String(80))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Facilitador(UUIDPrimaryKey, Timestamped, Base):
    """
    Operador de awareness del cliente. Autenticación distinta a la del usuario.
    Crea personajes y configura sesiones, pero NUNCA ve respuestas individuales.
    """

    __tablename__ = "facilitadores"

    organizacion_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("organizaciones.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    es_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
