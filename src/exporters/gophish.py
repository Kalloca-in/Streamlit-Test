"""Exportador formato GoPhish.

GoPhish acepta importación de templates y landing pages. Producimos un JSON
que el operador puede cargar manualmente en su instancia GoPhish del cliente.

Placeholders:
- `{{.URL}}` — el link trackeado que GoPhish reemplaza
- `{{.Tracker}}` — pixel de tracking
- `{{.FirstName}}` — nombre del destinatario (si está en la lista)

Mapeamos `{{TRACKING_LINK}}` (lo que devuelve nuestro generador) a `{{.URL}}`.
"""

from __future__ import annotations

from typing import Any

from src.exporters.html_pkg import build_email_html, build_landing_html


def to_gophish_template(template: dict[str, Any]) -> dict[str, Any]:
    body = template["body"].replace("{{TRACKING_LINK}}", "{{.URL}}")

    if template["vector"] == "email":
        html = build_email_html(template).replace("{{TRACKING_LINK}}", "{{.URL}}")
        # Append GoPhish tracking pixel
        html = html.replace("</body>", "{{.Tracker}}</body>")
        return {
            "name": f"{template['id']} - {template['topic_title'][:60]}",
            "subject": template.get("subject") or template["topic_title"],
            "html": html,
            "text": body,
            "envelope_sender": (
                f"{template['sender_display_name']} "
                f"<{template['sender_local_part']}@{template['sender_domain']}>"
            ),
        }
    # SMS y Teams: GoPhish no los soporta nativamente; los exportamos como
    # plantillas de texto plano para que el operador los use con su tooling.
    return {
        "name": f"{template['id']} - {template['topic_title'][:60]}",
        "subject": f"[{template['vector'].upper()}] {template['topic_title'][:80]}",
        "html": f"<pre>{body}</pre>",
        "text": body,
        "envelope_sender": template["sender_display_name"],
    }


def to_gophish_landing(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": f"{template['id']} - Landing",
        "html": build_landing_html(template),
        "capture_credentials": False,
        "capture_passwords": False,
        "redirect_url": "",
    }


def export_campaign(
    *,
    campaign_name: str,
    operator: dict[str, Any],
    alcance: dict[str, Any],
    templates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "campaign_name": campaign_name,
        "metadata": {
            "operator": operator.get("nombre"),
            "client": operator.get("cliente"),
            "folio": operator.get("folio"),
            "sandbox_domain": alcance["sandbox_domain"],
            "sector": alcance["sector"],
            "templates_count": len(templates),
        },
        "templates": [to_gophish_template(t) for t in templates],
        "landing_pages": [
            to_gophish_landing(t) for t in templates if t["vector"] == "email"
        ],
    }
