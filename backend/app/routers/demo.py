"""Level 11 — Demonstration. Pre-scripted, observed, not played."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

from app.data_catalogs import organizational_controls

router = APIRouter(prefix="/demo", tags=["demo"])

_SCRIPT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "demo_nivel11.json"


def _load_script() -> dict:
    with _SCRIPT_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/nivel-11")
async def demo_level_11():
    script = _load_script()
    controls_by_code = {c["code"]: c for c in organizational_controls()}
    closing = script["closing"]
    enriched = []
    for entry in closing["controls_that_would_have_stopped_it"]:
        ctl = controls_by_code.get(entry["code"], {})
        enriched.append({**entry, "display_name": ctl.get("display_name"), "description": ctl.get("description")})
    return {
        "title": script["title"],
        "description": script["description"],
        "character_code": script["character_code"],
        "archetype": script["archetype"],
        "objective": script["objective"],
        "script": script["script"],
        "closing": {
            "headline": closing["headline"],
            "controls_that_would_have_stopped_it": enriched,
        },
    }
