from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from pathlib import Path


def _safe_text(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_pdf_report(output_path, batch_info, image_result, risk_result, human_decision, notes_summary, image_path=None):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, leading=24))
    styles.add(ParagraphStyle(name="SmallText", parent=styles["Normal"], fontSize=9, leading=12))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#1F4E79"), spaceBefore=10, spaceAfter=6))

    story = []

    # Title
    story.append(Paragraph("QualityVision AI", styles["CenterTitle"]))
    story.append(Paragraph("Manufacturing Quality Inspection Report", styles["CenterTitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 14))

    # Executive summary
    story.append(Paragraph("Executive Summary", styles["Section"]))
    summary_data = [
        ["Visual Defect", _safe_text(image_result["defect_label"])],
        ["Image Confidence", f"{image_result['confidence']}%"],
        ["Batch Risk", f"{risk_result['risk_label']} ({risk_result['risk_score']}/100)"],
        ["Final Inspector Status", _safe_text(human_decision["final_status"])],
    ]
    summary_table = Table(summary_data, colWidths=[170, 330])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Batch info
    story.append(Paragraph("1. Batch & Production Details", styles["Section"]))
    info_data = [["Field", "Value"]]
    for k, v in batch_info.items():
        info_data.append([_safe_text(k), _safe_text(v)])
    table = Table(info_data, colWidths=[170, 330])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Image
    story.append(Paragraph("2. Uploaded Product Image", styles["Section"]))
    if image_path and Path(image_path).exists():
        try:
            story.append(RLImage(str(image_path), width=4.5*inch, height=3.0*inch))
        except Exception:
            story.append(Paragraph("Image preview could not be embedded, but analysis was completed.", styles["Normal"]))
    else:
        story.append(Paragraph("No image preview available in report.", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Operator / Inspection Notes Summary", styles["Section"]))
    story.append(Paragraph(_safe_text(notes_summary), styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("4. AI Analysis", styles["Section"]))
    ai_data = [
        ["AI Output", "Result"],
        ["Defect Class", _safe_text(image_result["defect_label"])],
        ["Image Confidence", f"{image_result['confidence']}%"],
        ["Risk Label", _safe_text(risk_result["risk_label"])],
        ["Risk Score", f"{risk_result['risk_score']}/100"],
        ["AI Recommendation", _safe_text(risk_result["recommendation"])],
    ]
    ai_table = Table(ai_data, colWidths=[170, 330])
    ai_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(ai_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("5. Explainable AI — Key Influencing Factors", styles["Section"]))
    exp_data = [["Factor", "Influence"]]
    for feature, value in risk_result["feature_importance"].items():
        exp_data.append([_safe_text(feature), f"{round(value * 100, 1)}%"])
    exp_table = Table(exp_data, colWidths=[250, 250])
    exp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("6. Human-in-the-Loop Final Decision", styles["Section"]))
    decision_data = [
        ["Decision Field", "Value"],
        ["Inspector Decision", _safe_text(human_decision["decision_type"])],
        ["Final Status", _safe_text(human_decision["final_status"])],
        ["Final Action", _safe_text(human_decision["final_action"])],
        ["QA Action", _safe_text(human_decision["qa_action"])],
        ["Inspector Notes", _safe_text(human_decision["inspector_notes"])],
    ]
    decision_table = Table(decision_data, colWidths=[170, 330])
    decision_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(decision_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Report generated by QualityVision AI Co-Pilot. Final responsibility remains with the human quality inspector.", styles["SmallText"]))

    doc.build(story)
    return output_path
