"""Smoke test for the FastAPI app boot path."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_liveness(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readiness_returns_invariants(client):
    r = client.get("/readyz")
    assert r.status_code == 200
    body = r.json()
    # Even if redis is unreachable in CI, we still want the invariants visible.
    assert "session_ttl_seconds" in body
    assert body["aggregation_min_n"] >= 10
