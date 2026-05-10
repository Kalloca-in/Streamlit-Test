"""Genera un PDF brief con todas las plantillas de la campaña.

Uso interno del operador y del equipo de seguridad del cliente: documenta
qué se va a enviar, qué indicadores se busca enseñar, y cuál es el objetivo
de capacitación de cada plantilla.
"""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors


def build_pdf_bytes(
    *,
    campaign_name: str,
    operator: dict[str, Any],
    alcance: dict[str, Any],
    templates: list[dict[str, Any]],
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=campaign_name,
        author=operator.get("nombre", ""),
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.grey)

    story = []
    story.append(Paragraph(f"Campaña: {campaign_name}", h1))
    story.append(Paragraph(
        f"Cliente: <b>{operator.get('cliente', '')}</b> · "
        f"Operador: {operator.get('nombre', '')} · "
        f"Folio: {operator.get('folio', '')}",
        body,
    ))
    story.append(Paragraph(
        f"Sandbox domain: <b>{alcance['sandbox_domain']}</b> · "
        f"Sector: {alcance['sector']} · "
        f"Vigencia: {alcance['inicio']} a {alcance['fin']}",
        small,
    ))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(
        "<b>Importante:</b> esta plataforma no envía mensajes. Las plantillas "
        "documentadas aquí están preparadas para ser cargadas manualmente en "
        "la infraestructura de envío autorizada del cliente. Cada plantilla "
        "incluye los indicadores detectables que el debrief educativo debe "
        "cubrir si el colaborador hace clic.",
        body,
    ))
    story.append(Spacer(1, 0.5 * cm))

    for i, t in enumerate(templates, start=1):
        story.append(Paragraph(f"Plantilla {i} — {t['topic_title']}", h2))

        meta_data = [
            ["ID", t["id"]],
            ["Vector", t["vector"].upper()],
            ["Dificultad", f"Tier {t['difficulty_tier']}"],
            ["Riesgo evaluado", t["risk_level"]],
        ]
        if t["vector"] == "email":
            sender = f"{t['sender_display_name']} <{t['sender_local_part']}@{t['sender_domain']}>"
            meta_data.append(["Remitente", sender])
            if t.get("subject"):
                meta_data.append(["Asunto", t["subject"]])
        else:
            meta_data.append(["Remitente", t["sender_display_name"]])

        tbl = Table(meta_data, colWidths=[3.5 * cm, 13 * cm])
        tbl.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("<b>Cuerpo del mensaje:</b>", body))
        body_text = t["body"].replace("\n", "<br/>")
        story.append(Paragraph(body_text, body))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("<b>Indicadores detectables (debrief):</b>", body))
        for ind in t["detectable_indicators"]:
            story.append(Paragraph(f"• {ind}", body))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("<b>Landing educativa:</b>", body))
        story.append(Paragraph(t["landing_description"], body))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"<i>Objetivo de capacitación:</i> {t['training_objective']}",
            small,
        ))
        story.append(Spacer(1, 0.8 * cm))

    doc.build(story)
    return buf.getvalue()
