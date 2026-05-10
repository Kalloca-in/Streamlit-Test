"""
Log de safety. Registro inmutable de cada bloqueo del safety_filter.

Cada vez que el filtro pre-generación detecta una violación a un
principio no negociable (marca real, OSINT, dificultad > 3, línea roja
de contenido) se persiste un registro aquí. Es la trazabilidad que
respalda el cumplimiento ante el cliente y la LOPDP de Ecuador.
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSONType
from app.models._mixins import Timestamped, UUIDPrimaryKey


class SafetyLog(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "safety_logs"

    motivo: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    contexto: Mapped[str] = mapped_column(String(80), nullable=False)
    payload_extracto: Mapped[str | None] = mapped_column(Text)
    detalles: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
