"""Empaqueta toda la campaña en un ZIP descargable.

Estructura del ZIP:
- manifest.json
- gophish/campaign.json
- html/email_<id>.html
- html/landing_<id>.html
- html/sms_<id>.txt
- html/teams_<id>.txt
- brief.pdf
- README.txt
"""

from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any

from src.exporters import gophish, html_pkg, pdf_brief

README = """Paquete de Campaña de Awareness
==================================

Generado por la Plataforma de Awareness. Esta plataforma NO envía mensajes.
El paquete contiene los artefactos para que tu equipo cargue manualmente la
campaña en la infraestructura de envío autorizada del cliente.

Contenido:
- manifest.json: metadata de la campaña.
- gophish/campaign.json: importable en GoPhish (templates + landing pages).
- html/: HTMLs y textos por plantilla, listos para tooling alternativo.
- brief.pdf: documento de referencia para el equipo de seguridad y debrief.

Recordatorio:
- Verificá que el dominio remitente declarado está bajo control del cliente.
- El envío debe estar autorizado por contrato vigente.
- Los indicadores detectables documentados son la base del debrief educativo
  posterior. No los descartes.
"""


def build_zip(
    *,
    campaign_name: str,
    operator: dict[str, Any],
    alcance: dict[str, Any],
    templates: list[dict[str, Any]],
) -> bytes:
    if not templates:
        raise ValueError("No hay plantillas para exportar.")

    manifest = {
        "campaign_name": campaign_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "operator": {k: operator.get(k) for k in ("nombre", "cliente", "folio")},
        "alcance": {
            "sandbox_domain": alcance["sandbox_domain"],
            "sector": alcance["sector"],
            "tamano": alcance["tamano"],
            "departamentos": alcance.get("departamentos", []),
            "vigencia": {
                "inicio": str(alcance["inicio"]),
                "fin": str(alcance["fin"]),
            },
        },
        "templates_summary": [
            {
                "id": t["id"],
                "topic": t["topic_title"],
                "vector": t["vector"],
                "difficulty_tier": t["difficulty_tier"],
                "risk_level": t["risk_level"],
            }
            for t in templates
        ],
    }

    gophish_payload = gophish.export_campaign(
        campaign_name=campaign_name,
        operator=operator,
        alcance=alcance,
        templates=templates,
    )

    pdf_bytes = pdf_brief.build_pdf_bytes(
        campaign_name=campaign_name,
        operator=operator,
        alcance=alcance,
        templates=templates,
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", README)
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        zf.writestr(
            "gophish/campaign.json",
            json.dumps(gophish_payload, ensure_ascii=False, indent=2),
        )
        zf.writestr("brief.pdf", pdf_bytes)
        for t in templates:
            if t["vector"] == "email":
                zf.writestr(
                    f"html/email_{t['id']}.html",
                    html_pkg.build_email_html(t),
                )
                zf.writestr(
                    f"html/landing_{t['id']}.html",
                    html_pkg.build_landing_html(t),
                )
            elif t["vector"] == "sms":
                zf.writestr(
                    f"html/sms_{t['id']}.txt",
                    html_pkg.build_sms_text(t),
                )
            elif t["vector"] == "teams":
                zf.writestr(
                    f"html/teams_{t['id']}.txt",
                    html_pkg.build_teams_text(t),
                )

    return buf.getvalue()
