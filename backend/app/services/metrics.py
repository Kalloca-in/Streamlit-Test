"""Aggregated metrics — n>=10 threshold enforced on read.

Writes are bucketed by (iso_year, iso_week, org_slug, level, archetype,
defender_kind, result). Each session ever stored increments a shared
counter; no individual row is recoverable.

Reads return zero data unless `n >= AGGREGATION_MIN_N` for the bucket.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import OperationalError

from app.config import get_settings
from app.db.models import HookOutcome, SessionOutcome
from app.db.session import get_sessionmaker
from app.models.defense import DefenseModel
from app.models.session import SessionState

DEFAULT_ORG = "_anonymous_"


def _iso_bucket(now: datetime | None = None) -> tuple[int, int]:
    n = now or datetime.now(timezone.utc)
    iso = n.isocalendar()
    return iso.year, iso.week


async def record_session_outcome(state: SessionState, *, org_slug: str | None) -> None:
    org = org_slug or DEFAULT_ORG
    iso_year, iso_week = _iso_bucket()
    sm = get_sessionmaker()
    try:
        async with sm() as db:
            stmt = pg_insert(SessionOutcome).values(
                iso_year=iso_year,
                iso_week=iso_week,
                org_slug=org,
                level=state.level,
                archetype=state.attacker.archetype.value,
                defender_kind=state.defender.kind.value,
                result=state.status.value,
                n=1,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    "iso_year",
                    "iso_week",
                    "org_slug",
                    "level",
                    "archetype",
                    "defender_kind",
                    "result",
                ],
                set_={"n": SessionOutcome.n + 1},
            )
            await db.execute(stmt)
            await db.commit()
    except OperationalError:
        # Postgres unavailable — metrics are non-critical.
        return


async def record_hook_outcomes(defense: DefenseModel, *, org_slug: str | None) -> None:
    org = org_slug or DEFAULT_ORG
    iso_year, iso_week = _iso_bucket()
    sm = get_sessionmaker()
    keys = set(defense.hook_resist_counts) | set(defense.hook_accept_counts)
    if not keys:
        return
    try:
        async with sm() as db:
            for hook in keys:
                accepted = defense.hook_accept_counts.get(hook, 0)
                rejected = defense.hook_resist_counts.get(hook, 0)
                stmt = pg_insert(HookOutcome).values(
                    iso_year=iso_year,
                    iso_week=iso_week,
                    org_slug=org,
                    hook=hook.value,
                    accepted_n=accepted,
                    rejected_n=rejected,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["iso_year", "iso_week", "org_slug", "hook"],
                    set_={
                        "accepted_n": HookOutcome.accepted_n + accepted,
                        "rejected_n": HookOutcome.rejected_n + rejected,
                    },
                )
                await db.execute(stmt)
            await db.commit()
    except OperationalError:
        return


async def aggregated_capture_rate_by_archetype(*, org_slug: str) -> list[dict]:
    """Returns per-archetype capture rate for the given org, but ONLY for
    archetypes whose total session count >= AGGREGATION_MIN_N. Buckets
    below threshold are suppressed entirely."""
    threshold = get_settings().aggregation_min_n
    sm = get_sessionmaker()
    async with sm() as db:
        stmt = (
            select(
                SessionOutcome.archetype,
                func.sum(SessionOutcome.n).label("total"),
                func.sum(
                    case((SessionOutcome.result == "captured", SessionOutcome.n), else_=0)
                ).label("captures"),
            )
            .where(SessionOutcome.org_slug == org_slug)
            .group_by(SessionOutcome.archetype)
        )
        rows = (await db.execute(stmt)).all()
    out = []
    for row in rows:
        total = int(row.total or 0)
        captures = int(row.captures or 0)
        if total < threshold:
            continue  # below n>=10 threshold — suppressed
        out.append(
            {
                "archetype": row.archetype,
                "total": total,
                "captures": captures,
                "capture_rate": round(captures / total, 3) if total else 0.0,
            }
        )
    return out


async def aggregated_hook_rates(*, org_slug: str) -> list[dict]:
    threshold = get_settings().aggregation_min_n
    sm = get_sessionmaker()
    async with sm() as db:
        stmt = (
            select(
                HookOutcome.hook,
                func.sum(HookOutcome.accepted_n).label("accepted"),
                func.sum(HookOutcome.rejected_n).label("rejected"),
            )
            .where(HookOutcome.org_slug == org_slug)
            .group_by(HookOutcome.hook)
        )
        rows = (await db.execute(stmt)).all()
    out = []
    for row in rows:
        accepted = int(row.accepted or 0)
        rejected = int(row.rejected or 0)
        n = accepted + rejected
        if n < threshold:
            continue
        out.append(
            {
                "hook": row.hook,
                "accepted": accepted,
                "rejected": rejected,
                "n": n,
                "acceptance_rate": round(accepted / n, 3) if n else 0.0,
            }
        )
    return out
