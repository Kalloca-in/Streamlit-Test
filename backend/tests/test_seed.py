"""
Tests del seed.

Verifican que:
- Hay 6 personajes y 6 Días Triples.
- Cada personaje cubre un arquetipo distinto.
- Cada Día Triple usa un gancho psicológico distinto.
- Todos los Días Triples cumplen los esquemas Pydantic estrictos.
- TODOS pasan validate_dia_triple_safe (i.e. ningún seed con marca real,
  línea roja, dificultad excedida o slug no catalogado).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.enums import Arquetipo, GanchoPsicologico
from app.schemas.dia_triple import DiaTripleCreate
from app.schemas.personaje import PersonajeCreate
from app.services.safety_filter import validate_dia_triple_safe

SEED_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "seed_personajes.json"


@pytest.fixture(scope="module")
def seed_data():
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_seed_contiene_6_entradas(seed_data):
    assert len(seed_data) == 6


def test_seed_arquetipos_distintos(seed_data):
    arquetipos = [e["personaje"]["arquetipo"] for e in seed_data]
    assert len(set(arquetipos)) == 6
    # cubre los 6 arquetipos del briefing
    assert set(arquetipos) == {a.value for a in Arquetipo}


def test_seed_ganchos_distintos(seed_data):
    ganchos = [e["dia_triple"]["gancho_psicologico_raiz"] for e in seed_data]
    assert len(set(ganchos)) == 6
    for g in ganchos:
        assert g in {x.value for x in GanchoPsicologico}


def test_seed_personajes_validos(seed_data):
    for entry in seed_data:
        PersonajeCreate(**entry["personaje"])  # raise si inválido


def test_seed_dias_triples_pasan_safety_filter(seed_data):
    for entry in seed_data:
        # personaje_id es opcional aquí; se asigna en runtime al crear.
        dt_dict = entry["dia_triple"] | {
            "personaje_id": "00000000-0000-0000-0000-000000000000"
        }
        dt = DiaTripleCreate(**dt_dict)
        validate_dia_triple_safe(dt, contexto="test_seed")  # no levanta
