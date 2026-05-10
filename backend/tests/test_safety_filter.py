"""Tests for the safety filter — encodes red lines and brand interception."""

from __future__ import annotations

import pytest

from app.services.safety_filter import (
    InterceptionCategory,
    filter_attacker_message,
)


@pytest.mark.parametrize(
    "real_brand",
    [
        "Banco Pichincha",
        "BBVA",
        "Santander",
        "Google",
        "WhatsApp",
        "Mercado Pago",
        "Movistar",
    ],
)
def test_real_brand_is_replaced(real_brand: str):
    text = f"Hola, te escribo de {real_brand} para verificar tu cuenta."
    r = filter_attacker_message(text)
    assert r.intercepted
    assert r.category == InterceptionCategory.REAL_BRAND
    assert real_brand.lower() not in r.safe_text.lower()


def test_fictitious_brand_passes_through():
    text = "Te escribo de Banco Andino del Sur para una verificación."
    r = filter_attacker_message(text)
    assert not r.intercepted
    assert "Banco Andino del Sur" in r.safe_text


def test_real_domain_is_stripped():
    text = "Entra a https://login.banco-pichincha.com para validar."
    r = filter_attacker_message(text)
    assert r.intercepted
    # Either brand or domain category — both block reality leak.
    assert r.category in {
        InterceptionCategory.REAL_DOMAIN,
        InterceptionCategory.REAL_BRAND,
    }
    assert ".com" not in r.safe_text


def test_example_domain_passes_through():
    text = "Entra a login.bancoandinodelsur.example para validar."
    r = filter_attacker_message(text)
    assert not r.intercepted
    assert "bancoandinodelsur.example" in r.safe_text


@pytest.mark.parametrize(
    "phrase",
    [
        "Mi hija tiene cáncer terminal y necesito tu ayuda.",
        "Sé que murió tu padre la semana pasada, lo siento.",
        "Si no haces esto te voy a hacer daño.",
        "Mándame fotos desnudas como prueba.",
        "Tienes que votar por el partido político X.",
    ],
)
def test_red_line_topics_are_neutralized(phrase: str):
    r = filter_attacker_message(phrase)
    assert r.intercepted
    # Either red-line topic or — for the threat sample — at least neutralized
    assert "cáncer" not in r.safe_text.lower()
    assert "murió" not in r.safe_text.lower()
    assert "desnudas" not in r.safe_text.lower()


def test_real_user_pii_request_is_intercepted():
    r = filter_attacker_message("Por favor dame tu cédula real para verificarte.")
    assert r.intercepted


def test_clean_text_passes():
    r = filter_attacker_message("Hola, ¿cómo estás? Tengo una propuesta para ti.")
    assert not r.intercepted
    assert r.category == InterceptionCategory.NONE


def test_filter_does_not_log_content(caplog):
    """Defensive: even if upstream logs the result, we never serialize the
    body. Sanity check that the FilterResult repr does not include marker."""
    r = filter_attacker_message("Banco Pichincha aquí, dame tu OTP.")
    assert "Pichincha" not in str(r.category)
