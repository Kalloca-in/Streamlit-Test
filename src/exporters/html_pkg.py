"""Renderiza emails y landings como HTML standalone.

El email HTML se diseña simple — texto plano envuelto en estructura mínima —
porque las plataformas reales de phishing simulado (GoPhish, KnowBe4) suelen
re-renderizar. Lo que importa es el contenido y el placeholder de tracking.

La landing es una página educativa que el colaborador ve si hace clic.
Lista los indicadores que debería haber detectado y el objetivo de
capacitación. Tono no-shaming.
"""

from __future__ import annotations

import html
from typing import Any


def _esc(text: str) -> str:
    return html.escape(text or "")


def build_email_html(template: dict[str, Any]) -> str:
    body = _esc(template["body"]).replace("\n", "<br>\n")
    subject = _esc(template.get("subject") or "")
    sender = (
        f"{_esc(template['sender_display_name'])} &lt;"
        f"{_esc(template['sender_local_part'])}@{_esc(template['sender_domain'])}&gt;"
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{subject}</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 24px auto; padding: 0 16px; color: #222; line-height: 1.5; }}
.meta {{ color: #666; font-size: 13px; border-bottom: 1px solid #eee; padding-bottom: 12px; margin-bottom: 16px; }}
.meta strong {{ color: #222; }}
</style>
</head>
<body>
<div class="meta">
<div><strong>De:</strong> {sender}</div>
<div><strong>Asunto:</strong> {subject}</div>
</div>
{body}
</body>
</html>"""


def build_sms_text(template: dict[str, Any]) -> str:
    return template["body"]


def build_teams_text(template: dict[str, Any]) -> str:
    return (
        f"De: {template['sender_display_name']}\n"
        f"\n"
        f"{template['body']}"
    )


def build_landing_html(template: dict[str, Any]) -> str:
    indicators_html = "\n".join(
        f"<li>{_esc(ind)}</li>" for ind in template["detectable_indicators"]
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Simulación de phishing — Material educativo</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; max-width: 720px; margin: 32px auto; padding: 0 24px; color: #222; line-height: 1.6; }}
h1 {{ color: #1a4d8f; }}
h2 {{ color: #333; margin-top: 28px; }}
.callout {{ background: #f0f4fa; border-left: 4px solid #1a4d8f; padding: 16px 20px; margin: 20px 0; border-radius: 4px; }}
.indicators {{ background: #fff8e1; padding: 16px 20px; border-radius: 4px; }}
.indicators ul {{ margin: 8px 0 0 0; padding-left: 24px; }}
.objective {{ color: #555; font-style: italic; margin-top: 24px; padding-top: 16px; border-top: 1px solid #eee; }}
</style>
</head>
<body>
<h1>Esto era una simulación de phishing</h1>
<div class="callout">
<p><strong>No te preocupes — no se comprometió nada.</strong> Esta página es parte
de un programa de awareness autorizado por tu organización. El objetivo es
ayudarte a reconocer ataques reales antes de que causen daño.</p>
</div>

<h2>Qué deberías haber notado</h2>
<div class="indicators">
<p>Esta simulación tenía las siguientes señales detectables:</p>
<ul>
{indicators_html}
</ul>
</div>

<h2>Cómo verificar en el futuro</h2>
<p>{_esc(template['landing_description'])}</p>

<p class="objective">Objetivo de capacitación: {_esc(template['training_objective'])}</p>
</body>
</html>"""
