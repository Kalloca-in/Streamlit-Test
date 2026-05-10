"""Smoke tests for the critical HTTP endpoints (excluding WebSocket)."""

from __future__ import annotations

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from app.deps import get_session_store
from app.main import create_app
from app.services.session_store import SessionStore


@pytest.fixture
def client():
    app = create_app()
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    def _override():
        return SessionStore(redis=fake, ttl_seconds=60)

    app.dependency_overrides[get_session_store] = _override
    return TestClient(app)


def test_catalogs_endpoint(client):
    r = client.get("/sessions/catalogs")
    assert r.status_code == 200
    body = r.json()
    assert len(body["archetypes"]) == 6
    assert 6 <= len(body["universal_characters"]) <= 8
    assert len(body["organizational_controls"]) >= 5


def test_demo_level_11_endpoint(client):
    r = client.get("/demo/nivel-11")
    assert r.status_code == 200
    body = r.json()
    assert body["title"]
    assert len(body["script"]) > 0
    assert body["closing"]["headline"]
    assert len(body["closing"]["controls_that_would_have_stopped_it"]) >= 3


def test_create_session_self_level_3(client):
    r = client.post("/sessions", json={"level": 3})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["level"] == 3
    assert body["special_mode"] == "none"
    # Random levels do not reveal the archetype to the user.
    assert body["archetype"] is None


def test_create_session_level_8_requires_character(client):
    r = client.post("/sessions", json={"level": 8})
    assert r.status_code == 422


def test_create_session_level_8_with_character(client):
    r = client.post(
        "/sessions",
        json={
            "level": 8,
            "archetype": "experto_tecnico",
            "defender_kind": "universal_character",
            "universal_character_code": "soporte_ti",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["archetype"] == "experto_tecnico"
    assert body["defender"]["character"]["code"] == "soporte_ti"


def test_create_session_level_12_caja_negra(client):
    r = client.post(
        "/sessions",
        json={
            "level": 12,
            "archetype": "autoridad_apurada",
            "defender_kind": "universal_character",
            "universal_character_code": "contador_general",
        },
    )
    assert r.status_code == 200
    assert r.json()["special_mode"] == "caja_negra"


def test_facilitator_requires_token(client):
    r = client.post("/facilitator/orgs", json={"slug": "x", "display_name": "X"})
    assert r.status_code == 401


def test_facilitator_rejects_bad_token_shape(client):
    r = client.post(
        "/facilitator/orgs",
        json={"slug": "x", "display_name": "X"},
        headers={"X-Facilitator-Token": "wrong"},
    )
    assert r.status_code == 403
