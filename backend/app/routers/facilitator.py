"""Facilitator endpoints — characters CRUD + aggregated dashboards.

Authentication is intentionally minimal here (header token). Production
deployments should layer real OIDC in front. The point is to keep the
contract honest: facilitators only ever see aggregated metrics with
n >= AGGREGATION_MIN_N. That guarantee is enforced at the service layer
(`app.services.metrics`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError

from app.db.models import CorporateCharacter, FacilitatorOrg
from app.db.session import get_db
from app.services.metrics import (
    aggregated_capture_rate_by_archetype,
    aggregated_hook_rates,
)

router = APIRouter(prefix="/facilitator", tags=["facilitator"])


def _auth(x_facilitator_token: str | None = Header(default=None)) -> str:
    """Tokens are placeholder. In production, replace with OIDC introspection."""
    if not x_facilitator_token:
        raise HTTPException(401, "Missing X-Facilitator-Token.")
    if not x_facilitator_token.startswith("fac_"):
        raise HTTPException(403, "Invalid token shape.")
    return x_facilitator_token


class OrgIn(BaseModel):
    slug: str
    display_name: str
    industry: str | None = None


class CharacterIn(BaseModel):
    code: str
    display_name: str
    role_title: str
    fictional_context: str
    hierarchy_level: str | None = None


@router.post("/orgs")
async def create_org(
    payload: OrgIn,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(_auth),
):
    org = FacilitatorOrg(**payload.model_dump())
    db.add(org)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(409, "Org with that slug already exists.")
    await db.refresh(org)
    return {"id": org.id, "slug": org.slug}


@router.post("/orgs/{slug}/characters")
async def create_character(
    slug: str,
    payload: CharacterIn,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(_auth),
):
    org = (await db.execute(select(FacilitatorOrg).where(FacilitatorOrg.slug == slug))).scalar_one_or_none()
    if org is None:
        raise HTTPException(404, "Org not found.")
    char = CorporateCharacter(org_id=org.id, **payload.model_dump())
    db.add(char)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(409, "Character code already exists for this org.")
    await db.refresh(char)
    return {"id": char.id, "code": char.code}


@router.get("/orgs/{slug}/characters")
async def list_characters(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _token: str = Depends(_auth),
):
    rows = (
        await db.execute(
            select(CorporateCharacter)
            .join(FacilitatorOrg)
            .where(FacilitatorOrg.slug == slug)
        )
    ).scalars().all()
    return [
        {
            "code": c.code,
            "display_name": c.display_name,
            "role_title": c.role_title,
            "fictional_context": c.fictional_context,
            "hierarchy_level": c.hierarchy_level,
        }
        for c in rows
    ]


@router.get("/orgs/{slug}/metrics/captures")
async def metrics_captures(
    slug: str,
    _token: str = Depends(_auth),
):
    try:
        return {"buckets": await aggregated_capture_rate_by_archetype(org_slug=slug)}
    except OperationalError:
        raise HTTPException(503, "Métricas no disponibles temporalmente.")


@router.get("/orgs/{slug}/metrics/hooks")
async def metrics_hooks(
    slug: str,
    _token: str = Depends(_auth),
):
    try:
        return {"buckets": await aggregated_hook_rates(org_slug=slug)}
    except OperationalError:
        raise HTTPException(503, "Métricas no disponibles temporalmente.")
