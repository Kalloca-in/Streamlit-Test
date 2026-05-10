"""Tests for configuration guard rails — these encode the non-negotiables."""

from __future__ import annotations

import pytest

from app.config import Settings


def test_ttl_ceiling_rejects_over_30_minutes(monkeypatch):
    monkeypatch.setenv("CIBERSPAR_ENV", "dev")
    monkeypatch.setenv("SESSION_TTL_SECONDS", "1801")
    with pytest.raises(ValueError, match="30-minute ceiling"):
        Settings()


def test_prod_must_use_full_ttl(monkeypatch):
    monkeypatch.setenv("CIBERSPAR_ENV", "prod")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("SESSION_TTL_SECONDS", "60")
    monkeypatch.setenv("AGGREGATION_MIN_N", "10")
    with pytest.raises(ValueError, match="full 30-minute"):
        Settings()


def test_prod_must_keep_aggregation_floor(monkeypatch):
    monkeypatch.setenv("CIBERSPAR_ENV", "prod")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("SESSION_TTL_SECONDS", "1800")
    monkeypatch.setenv("AGGREGATION_MIN_N", "5")
    with pytest.raises(ValueError, match="AGGREGATION_MIN_N"):
        Settings()


def test_dev_can_shorten_ttl_for_iteration(monkeypatch):
    monkeypatch.setenv("CIBERSPAR_ENV", "dev")
    monkeypatch.setenv("SESSION_TTL_SECONDS", "60")
    s = Settings()
    assert s.session_ttl_seconds == 60
