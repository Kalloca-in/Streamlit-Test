"""Tests para los exportadores.

Verifican que el ZIP de campaña sale bien formado, incluye todos los
artefactos esperados y respeta el constraint de sandbox domain.
"""

from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.exporters import bundle, gophish, html_pkg


OPERATOR = {
    "nombre": "operadora-test",
    "cliente": "ACME Corp",
    "folio": "ENG-2025-001",
}

ALCANCE = {
    "sector": "Tecnología",
    "tamano": "250–1.000",
    "sandbox_domain": "awareness-acme.com",
    "departamentos": ["IT", "Finanzas"],
    "topicos_excluidos": ["Salud o enfermedad de familiares"],
    "inicio": "2025-01-01",
    "fin": "2025-12-31",
}

TEMPLATE_EMAIL = {
    "id": "tpl_001",
    "topic_idx": 0,
    "topic_title": "Reset de MFA por mesa de ayuda",
    "vector": "email",
    "difficulty_tier": 2,
    "risk_level": "bajo",
    "subject": "Acción requerida: validá tu MFA",
    "body": "Estimado equipo,\n\nNecesitamos que valides tu MFA en {{TRACKING_LINK}}.\n\nMesa de Ayuda IT",
    "sender_display_name": "Mesa de Ayuda IT",
    "sender_local_part": "it-helpdesk",
    "sender_domain": "awareness-acme.com",
    "detectable_indicators": [
        "El dominio remitente (awareness-acme.com) no es el dominio corporativo real (acme.com).",
        "Saludo genérico al equipo en lugar del nombre.",
    ],
    "landing_description": "Verificá siempre que el dominio remitente coincida con el corporativo antes de actuar.",
    "training_objective": "Reconocer dominios sandbox vs dominios corporativos.",
    "created_at": "2025-01-15T10:00:00+00:00",
}

TEMPLATE_SMS = {
    **TEMPLATE_EMAIL,
    "id": "tpl_002",
    "vector": "sms",
    "subject": None,
    "sender_local_part": None,
    "body": "ACME-IT: validá MFA acá: {{TRACKING_LINK}}",
}


def test_bundle_zip_has_all_artifacts():
    zip_bytes = bundle.build_zip(
        campaign_name="test-campaign",
        operator=OPERATOR,
        alcance=ALCANCE,
        templates=[TEMPLATE_EMAIL, TEMPLATE_SMS],
    )
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = set(zf.namelist())
        assert "README.txt" in names
        assert "manifest.json" in names
        assert "gophish/campaign.json" in names
        assert "brief.pdf" in names
        assert "html/email_tpl_001.html" in names
        assert "html/landing_tpl_001.html" in names
        assert "html/sms_tpl_002.txt" in names


def test_bundle_manifest_does_not_include_message_content():
    """El manifest tiene metadata de cada template pero NO el contenido del
    mensaje. El contenido vive en los HTMLs/PDF, no en metadata indexable."""
    zip_bytes = bundle.build_zip(
        campaign_name="test", operator=OPERATOR, alcance=ALCANCE,
        templates=[TEMPLATE_EMAIL],
    )
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        manifest = json.loads(zf.read("manifest.json"))
    summary = manifest["templates_summary"][0]
    assert "body" not in summary
    assert "subject" not in summary
    assert summary["id"] == "tpl_001"
    assert summary["vector"] == "email"


def test_gophish_email_replaces_tracking_placeholder():
    payload = gophish.to_gophish_template(TEMPLATE_EMAIL)
    assert "{{TRACKING_LINK}}" not in payload["html"]
    assert "{{TRACKING_LINK}}" not in payload["text"]
    assert "{{.URL}}" in payload["html"]
    assert "{{.URL}}" in payload["text"]
    assert "{{.Tracker}}" in payload["html"]


def test_gophish_envelope_uses_sandbox_domain():
    payload = gophish.to_gophish_template(TEMPLATE_EMAIL)
    assert "awareness-acme.com" in payload["envelope_sender"]


def test_landing_lists_all_indicators():
    landing = html_pkg.build_landing_html(TEMPLATE_EMAIL)
    for ind in TEMPLATE_EMAIL["detectable_indicators"]:
        # html.escape may transform some chars; check first 30 chars
        assert ind[:30].split("(")[0].strip() in landing or ind[:30] in landing


def test_email_html_contains_sandbox_domain():
    rendered = html_pkg.build_email_html(TEMPLATE_EMAIL)
    assert "awareness-acme.com" in rendered
    assert "it-helpdesk" in rendered


def test_bundle_rejects_empty_templates():
    with pytest.raises(ValueError):
        bundle.build_zip(
            campaign_name="empty",
            operator=OPERATOR,
            alcance=ALCANCE,
            templates=[],
        )
