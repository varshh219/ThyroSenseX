import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)


# ── Color palette ──────────────────────────────────────────────
COLOR_BG        = colors.HexColor("#0a0e14")
COLOR_ACCENT    = colors.HexColor("#4f8dff")
COLOR_GREEN     = colors.HexColor("#3ddc97")
COLOR_YELLOW    = colors.HexColor("#f0c040")
COLOR_RED       = colors.HexColor("#ff4f5e")
COLOR_TEXT      = colors.HexColor("#e8edf7")
COLOR_MUTED     = colors.HexColor("#7a90b8")
COLOR_CARD      = colors.HexColor("#161c28")
COLOR_BORDER    = colors.HexColor("#1e2d45")
COLOR_WHITE     = colors.white


def get_prediction_color(prediction):
    return {
        "Normal":          COLOR_GREEN,
        "Hypothyroidism":  COLOR_YELLOW,
        "Hyperthyroidism": COLOR_RED,
    }.get(prediction, COLOR_TEXT)


def generate_report(
    result: dict,
    output_dir="reports/output",
    patient: dict = None
) -> str:
    """
    Generates a PDF diagnostic report.

    Args:
        result    : dict with prediction, confidence, probabilities
        output_dir: folder to save the PDF
        patient   : dict with patient details (optional)

    Returns:
        path to the saved PDF file
    """

    os.makedirs(output_dir, exist_ok=True)

    # ── File name ──────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pid       = patient.get("id", "UNKNOWN") if patient else "UNKNOWN"
    filename  = f"ThyroSenseX_{pid}_{timestamp}.pdf"
    filepath  = os.path.join(output_dir, filename)

    # ── Document setup ─────────────────────────────────
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    # ── Styles ─────────────────────────────────────────
    style_title = ParagraphStyle(
        "title",
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=COLOR_ACCENT,
        spaceAfter=4,
    )
    style_subtitle = ParagraphStyle(
        "subtitle",
        fontSize=11,
        fontName="Helvetica",
        textColor=COLOR_MUTED,
        spaceAfter=12,
    )
    style_section = ParagraphStyle(
        "section",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=COLOR_MUTED,
        spaceBefore=16,
        spaceAfter=6,
        letterSpacing=1.5,
    )
    style_warning = ParagraphStyle(
        "warning",
        fontSize=9,
        fontName="Helvetica-Oblique",
        textColor=COLOR_MUTED,
        spaceAfter=6,
        leading=14,
    )

    # ── Content ────────────────────────────────────────
    story = []
    now   = datetime.now().strftime("%d %B %Y  %H:%M:%S")

    # ── Header ────────────────────────────────────────
    story.append(Paragraph("ThyroSenseX", style_title))
    story.append(Paragraph(
        "AI · IoT Based Non-Invasive Thyroid Detection System",
        style_subtitle
    ))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=COLOR_BORDER, spaceAfter=12
    ))

    # ── Patient + Session info ─────────────────────────
    story.append(Paragraph("PATIENT & SESSION INFORMATION", style_section))

    if patient:
        session_data = [
            ["Patient Name",  patient.get("name",    "—")],
            ["Patient ID",    patient.get("id",      "—")],
            ["Age / Gender",  f"{patient.get('age', '—')} yrs  ·  "
                              f"{patient.get('gender', '—')}"],
            ["Phone",         patient.get("phone",   "—")],
            ["Address",       patient.get("address", "—")],
            ["Date / Time",   now],
            ["Device ID",     result.get("device_id",    "TSX-RPZ2-0042")],
            ["Model Version", result.get("model_version","v2.1.4")],
            ["Scan Duration", result.get("scan_duration","43.7 s")],
        ]
    else:
        session_data = [
            ["Date / Time",   now],
            ["Device ID",     result.get("device_id",    "TSX-RPZ2-0042")],
            ["Model Version", result.get("model_version","v2.1.4")],
            ["Scan Duration", result.get("scan_duration","43.7 s")],
        ]

    session_table = Table(session_data, colWidths=[5*cm, 12*cm])
    session_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, -1), COLOR_CARD),
        ("TEXTCOLOR",      (0, 0), (0, -1),  COLOR_MUTED),
        ("TEXTCOLOR",      (1, 0), (1, -1),  COLOR_TEXT),
        ("FONTNAME",       (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COLOR_CARD, COLOR_BG]),
        ("TOPPADDING",     (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 8),
        ("LEFTPADDING",    (0, 0), (-1, -1), 12),
        ("GRID",           (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(session_table)

    # ── Prediction result ──────────────────────────────
    story.append(Paragraph("DIAGNOSTIC RESULT", style_section))

    prediction = result.get("prediction", "Unknown")
    confidence = result.get("confidence", 0.0)
    pred_color = get_prediction_color(prediction)

    risk_map = {
        "Normal":          ("Low",      COLOR_GREEN),
        "Hypothyroidism":  ("Moderate", COLOR_YELLOW),
        "Hyperthyroidism": ("High",     COLOR_RED),
    }
    risk_level, risk_color = risk_map.get(
        prediction, ("Unknown", COLOR_MUTED)
    )

    pred_data = [
        ["Prediction",     prediction],
        ["Confidence",     f"{confidence:.1f}%"],
        ["Risk Level",     risk_level],
        ["Recommendation", "Consult an endocrinologist for confirmation"],
    ]

    pred_table = Table(pred_data, colWidths=[5*cm, 12*cm])
    pred_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), COLOR_CARD),
        ("TEXTCOLOR",     (0, 0), (0, -1),  COLOR_MUTED),
        ("TEXTCOLOR",     (1, 0), (1, -1),  COLOR_TEXT),
        ("TEXTCOLOR",     (1, 0), (1, 0),   pred_color),
        ("TEXTCOLOR",     (1, 1), (1, 1),   pred_color),
        ("TEXTCOLOR",     (1, 2), (1, 2),   risk_color),
        ("TEXTCOLOR",     (1, 3), (1, 3),   COLOR_ACCENT),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",      (1, 0), (1, 0),   "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("FONTSIZE",      (1, 0), (1, 0),   13),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [COLOR_CARD, COLOR_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("GRID",          (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(pred_table)

    # ── Probability distribution ───────────────────────
    story.append(Paragraph("PROBABILITY DISTRIBUTION", style_section))

    probs     = result.get("probabilities", {
        "Normal": 0, "Hypothyroidism": 0, "Hyperthyroidism": 0
    })
    prob_data = [["Condition", "Probability"]]
    for name, pct in probs.items():
        prob_data.append([name, f"{pct:.1f}%"])

    prob_table = Table(prob_data, colWidths=[10*cm, 7*cm])
    prob_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  COLOR_ACCENT),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  COLOR_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",    (0, 1), (-1, -1), COLOR_CARD),
        ("TEXTCOLOR",     (0, 1), (-1, -1), COLOR_TEXT),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [COLOR_CARD, COLOR_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("ALIGN",         (1, 0), (1, -1),  "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(prob_table)

    # ── Extracted features ─────────────────────────────
    story.append(Paragraph("EXTRACTED FEATURES", style_section))

    features  = result.get("features", {
        "Pitch":        "148 Hz",
        "Jitter":       "1.2%",
        "Shimmer":      "3.8%",
        "HNR":          "18.4 dB",
        "Thermal Mean": "34.5 °C",
        "Thermal Max":  "35.2 °C",
        "Thermal Min":  "33.1 °C",
        "Facial Flags": "4 of 10",
    })
    feat_data = [["Feature", "Value"]]
    for k, v in features.items():
        feat_data.append([k, str(v)])

    feat_table = Table(feat_data, colWidths=[10*cm, 7*cm])
    feat_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  COLOR_CARD),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  COLOR_ACCENT),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",    (0, 1), (-1, -1), COLOR_BG),
        ("TEXTCOLOR",     (0, 1), (-1, -1), COLOR_TEXT),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [COLOR_CARD, COLOR_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("GRID",          (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(feat_table)

    # ── Signature line ─────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(
        width="100%", thickness=0.5,
        color=COLOR_BORDER, spaceAfter=8
    ))

    sig_data = [
        ["Reviewed by:", "Signature:"],
        ["", ""],
        ["Doctor / Clinician Name", "________________________"],
    ]
    sig_table = Table(sig_data, colWidths=[8.5*cm, 8.5*cm])
    sig_table.setStyle(TableStyle([
        ("TEXTCOLOR",    (0, 0), (-1, -1), COLOR_MUTED),
        ("FONTNAME",     (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(sig_table)

    # ── Disclaimer ─────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(
        width="100%", thickness=0.5,
        color=COLOR_BORDER, spaceAfter=8
    ))
    story.append(Paragraph(
        "⚠ DISCLAIMER: This report is generated by an AI-based screening "
        "tool and is intended for preliminary screening purposes only. "
        "Results must be confirmed by a licensed medical professional. "
        "Do not use this report as a substitute for professional medical advice.",
        style_warning
    ))
    story.append(Paragraph(
        f"Generated by ThyroSenseX v2.1.4  ·  {now}",
        style_warning
    ))

    # ── Build PDF ──────────────────────────────────────
    doc.build(story)
    print(f"✓ PDF saved → {filepath}")
    return filepath