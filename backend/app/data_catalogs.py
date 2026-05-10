"""In-memory loader for the JSON catalogs under `backend/data/`.

Catalogs are loaded once at import time and cached. They are static IP and
ship with the codebase; reloading happens on process restart.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.models.attacker import AttackerArchetype, AttackerCard, AttackerObjective
from app.models.character import CharacterCard

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _read(filename: str) -> dict[str, Any]:
    with (_DATA_DIR / filename).open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache
def attacker_catalog() -> dict[AttackerArchetype, AttackerCard]:
    raw = _read("atacantes_arquetipos.json")
    out: dict[AttackerArchetype, AttackerCard] = {}
    for entry in raw["archetypes"]:
        card = AttackerCard.model_validate(entry)
        out[card.code] = card
    return out


@lru_cache
def attacker_objectives() -> dict[AttackerObjective, dict[str, str]]:
    raw = _read("atacantes_arquetipos.json")
    return {AttackerObjective(o["code"]): o for o in raw["objectives"]}


@lru_cache
def universal_characters() -> dict[str, CharacterCard]:
    raw = _read("personajes_universales.json")
    return {c["code"]: CharacterCard.model_validate(c) for c in raw["characters"]}


@lru_cache
def fictitious_brands() -> list[dict[str, str]]:
    return _read("marcas_ficticias.json")["brands"]


@lru_cache
def organizational_controls() -> list[dict[str, str]]:
    return _read("controles_organizacionales.json")["controls"]
