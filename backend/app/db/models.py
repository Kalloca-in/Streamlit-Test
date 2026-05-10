"""Persistent models — catalogs, facilitator config, aggregated metrics.

Schema design notes:

- `SessionOutcome` records are append-only counters keyed by coarse buckets
  (week, level, archetype, result). They carry no per-user identifier and
  no timestamp finer than the ISO week to make individual re-identification
  arithmetically impossible.
- The `n` column is an aggregate count. Reads enforce `n >= AGGREGATION_MIN_N`
  before returning anything (see `app.services.metrics`, Block 10).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FacilitatorOrg(Base):
    """A client organization whose facilitator can configure custom characters."""

    __tablename__ = "facilitator_orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    characters: Mapped[list["CorporateCharacter"]] = relationship(
        back_populates="org", cascade="all, delete-orphan"
    )


class CorporateCharacter(Base):
    """Fictional corporate character authored by a facilitator.

    No real OSINT. The fields below describe an *archetype* of role.
    """

    __tablename__ = "corporate_characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("facilitator_orgs.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role_title: Mapped[str] = mapped_column(String(200), nullable=False)
    fictional_context: Mapped[str] = mapped_column(Text, nullable=False)
    hierarchy_level: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    org: Mapped["FacilitatorOrg"] = relationship(back_populates="characters")

    __table_args__ = (UniqueConstraint("org_id", "code", name="uq_corp_char_org_code"),)


class SessionOutcome(Base):
    """Append-only aggregated counter. NO per-user data, ever.

    Each row is an aggregate `(iso_year, iso_week, org_slug, level, archetype,
    defender_kind, result) -> n`. Multiple sessions with identical bucketing
    increment `n`; no individual session is recoverable.
    """

    __tablename__ = "session_outcomes"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer(), "sqlite"), primary_key=True, autoincrement=True)
    iso_year: Mapped[int] = mapped_column(Integer, nullable=False)
    iso_week: Mapped[int] = mapped_column(Integer, nullable=False)
    org_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    archetype: Mapped[str] = mapped_column(String(64), nullable=False)
    defender_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    n: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "iso_year",
            "iso_week",
            "org_slug",
            "level",
            "archetype",
            "defender_kind",
            "result",
            name="uq_outcome_bucket",
        ),
    )


class HookOutcome(Base):
    """Aggregated tally of which psychological hooks land vs. get rejected.

    Bucketed exactly like SessionOutcome. No individual session reachable.
    """

    __tablename__ = "hook_outcomes"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer(), "sqlite"), primary_key=True, autoincrement=True)
    iso_year: Mapped[int] = mapped_column(Integer, nullable=False)
    iso_week: Mapped[int] = mapped_column(Integer, nullable=False)
    org_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    hook: Mapped[str] = mapped_column(String(64), nullable=False)
    accepted_n: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_n: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "iso_year", "iso_week", "org_slug", "hook", name="uq_hook_bucket"
        ),
    )


class SafetyInterception(Base):
    """Counter of safety_filter interceptions. Records that an interception
    happened in a given week + org + category — never the content."""

    __tablename__ = "safety_interceptions"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer(), "sqlite"), primary_key=True, autoincrement=True)
    iso_year: Mapped[int] = mapped_column(Integer, nullable=False)
    iso_week: Mapped[int] = mapped_column(Integer, nullable=False)
    org_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    n: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "iso_year",
            "iso_week",
            "org_slug",
            "category",
            name="uq_safety_bucket",
        ),
    )
