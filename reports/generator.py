import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle
)


def generate_report(result, output_dir="reports/output", patient=None, doctor=None):

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pid = patient.get("id", "UNKNOWN") if patient else "UNKNOWN"
    filepath = os.path.join(output_dir, f"ThyroSenseX_{pid}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    # ── STYLES ─────────────────────────────
    style_title = ParagraphStyle(
        "title", fontSize=18, fontName="Helvetica-Bold",
        textColor=colors.black, spaceAfter=12
    )

    style_section = ParagraphStyle(
        "section", fontSize=12, fontName="Helvetica-Bold",
        textColor=colors.black, spaceBefore=12, spaceAfter=6
    )

    style_text = ParagraphStyle(
        "text", fontSize=10, textColor=colors.black
    )

    story = []

    now = datetime.now().strftime("%d %B %Y, %H:%M")

    # ── HEADER ─────────────────────────────
    story.append(Paragraph("ThyroSenseX Diagnostic Report", style_title))

    # ── PATIENT DETAILS ────────────────────
    story.append(Paragraph("Patient Details", style_section))

    data = []

    if patient:
        data.extend([
            ["Name", patient.get("name", "—")],
            ["Patient ID", patient.get("id", "—")],
            ["Age / Gender", f"{patient.get('age')} / {patient.get('gender')}"],
            ["Weight", f"{patient.get('weight','—')} kg"],   # 🔥 ADDED
            ["Phone", patient.get("phone", "—")],
        ])

    if doctor:
        data.append(["Doctor", doctor.get("full_name", "—")])

    data.append(["Date", now])

    table = Table(data, colWidths=[5*cm, 11*cm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(table)

    # ── RESULT ─────────────────────────────
    story.append(Paragraph("Result", style_section))

    prediction = result.get("prediction", "—")
    confidence = result.get("confidence", 0)

    if confidence <= 1:
        confidence *= 100

    # 🔥 Risk Level Logic
    if prediction == "Normal":
        risk = "Low"
    elif prediction == "Hyperthyroidism":
        risk = "High"
    else:
        risk = "Moderate"

    result_table = Table([
        ["Prediction", prediction],
        ["Confidence", f"{confidence:.1f}%"],
        ["Risk Level", risk]   # 🔥 ADDED
    ], colWidths=[5*cm, 11*cm])

    result_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(result_table)

    # ── STATUS ─────────────────────────────
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"Status: The patient shows indications of {prediction}. "
        f"Clinical consultation is recommended for confirmation.",
        style_text
    ))

    doc.build(story)

    print("PDF saved:", filepath)
    return filepath