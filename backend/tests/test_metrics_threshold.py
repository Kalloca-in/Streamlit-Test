"""Aggregation threshold test — n>=10 must be enforced on read."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base
from app.db.models import HookOutcome, SessionOutcome
from app.services import metrics as metrics_module


@pytest.fixture
async def in_memory_db(monkeypatch):
    """Spin up an in-memory SQLite (compatible enough for our queries)."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    monkeypatch.setattr(metrics_module, "get_sessionmaker", lambda: sm)
    yield sm
    await engine.dispose()


async def _seed_outcomes(sm, *, n_per_archetype: dict[str, int], result: str = "captured"):
    async with sm() as db:
        for archetype, n in n_per_archetype.items():
            db.add(
                SessionOutcome(
                    iso_year=2026,
                    iso_week=18,
                    org_slug="acme",
                    level=5,
                    archetype=archetype,
                    defender_kind="self",
                    result=result,
                    n=n,
                )
            )
        await db.commit()


async def _seed_hooks(sm, hook: str, accepted: int, rejected: int):
    async with sm() as db:
        db.add(
            HookOutcome(
                iso_year=2026,
                iso_week=18,
                org_slug="acme",
                hook=hook,
                accepted_n=accepted,
                rejected_n=rejected,
            )
        )
        await db.commit()


@pytest.mark.asyncio
async def test_below_threshold_buckets_are_suppressed(in_memory_db):
    sm = in_memory_db
    await _seed_outcomes(sm, n_per_archetype={"complice": 9})
    out = await metrics_module.aggregated_capture_rate_by_archetype(org_slug="acme")
    assert out == []  # n=9 < 10 — fully suppressed


@pytest.mark.asyncio
async def test_at_or_above_threshold_returns_data(in_memory_db):
    sm = in_memory_db
    await _seed_outcomes(sm, n_per_archetype={"complice": 10, "insider": 7})
    out = await metrics_module.aggregated_capture_rate_by_archetype(org_slug="acme")
    archetypes_returned = {row["archetype"] for row in out}
    assert "complice" in archetypes_returned
    assert "insider" not in archetypes_returned


@pytest.mark.asyncio
async def test_hooks_below_threshold_suppressed(in_memory_db):
    sm = in_memory_db
    await _seed_hooks(sm, "autoridad", accepted=4, rejected=4)  # n=8
    out = await metrics_module.aggregated_hook_rates(org_slug="acme")
    assert out == []


@pytest.mark.asyncio
async def test_hooks_at_threshold_returned(in_memory_db):
    sm = in_memory_db
    await _seed_hooks(sm, "urgencia", accepted=6, rejected=4)  # n=10
    out = await metrics_module.aggregated_hook_rates(org_slug="acme")
    assert any(r["hook"] == "urgencia" for r in out)
