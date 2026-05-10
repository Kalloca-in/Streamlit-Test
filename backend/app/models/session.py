"""Session-state models. These objects live only in Redis with a TTL."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field

from app.models.attacker import AttackerInstance
from app.models.character import DefenderIdentity


class SessionStatus(StrEnum):
    ACTIVE = "active"
    CAPTURED = "captured"  # User gave the attacker what they wanted
    VICTORY = "victory"  # User legitimately shut the attacker out
    LEFT_DIGNIFIED = "left_dignified"  # User used "Salir con dignidad"
    TIMED_OUT = "timed_out"  # 30-min ceiling hit
    DEMO = "demo"  # Level 11 special


class SpecialMode(StrEnum):
    NONE = "none"
    DEMOSTRACION = "demostracion"  # Level 11
    CAJA_NEGRA = "caja_negra"  # Level 12


class TurnRole(StrEnum):
    ATTACKER = "attacker"
    DEFENDER = "defender"
    SYSTEM = "system"  # narrator events, control invocations, etc.


class TurnMessage(BaseModel):
    role: TurnRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    intercepted: bool = False  # True if safety_filter rewrote this message


class SessionState(BaseModel):
    """The full live state of one sparring session.

    Lives in Redis under key `session:{session_id}` with TTL = SESSION_TTL_SECONDS.
    """

    session_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.ACTIVE
    special_mode: SpecialMode = SpecialMode.NONE

    level: int = Field(ge=1, le=12)
    attacker: AttackerInstance
    defender: DefenderIdentity

    transcript: list[TurnMessage] = Field(default_factory=list)
    turn_count: int = 0

    # Indicates which controls (level 12) the user has invoked.
    invoked_controls: list[str] = Field(default_factory=list)

    def append(self, message: TurnMessage) -> None:
        self.transcript.append(message)
        if message.role in (TurnRole.ATTACKER, TurnRole.DEFENDER):
            self.turn_count += 1

    @property
    def elapsed_seconds(self) -> float:
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
