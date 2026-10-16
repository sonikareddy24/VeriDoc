"""Programmatic PDF report generation using ReportLab (BSD-3-Clause).
Generates an audit-ready verification and consistency summary report.
Never claims identity or fraud verdicts.
"""

import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)

from backend.app.schemas.session import SessionAnalysisResponse


def generate_pdf_report(analysis: SessionAnalysisResponse) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#991b1b"),
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("VeriDocs AI — Verification & Consistency Audit Report", title_style))
    elements.append(Paragraph(f"Generated at: {analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S UTC')} | Session ID: {analysis.session_id}", subtitle_style))
    elements.append(Spacer(1, 8))

    # Prominent Disclaimer Box
    disclaimer_text = (
        "<b>RESEARCH PROTOTYPE NOTICE:</b> This system assesses document consistency and evidence grounding "
        "using deterministic rules. It is NOT an authenticity, forensics, or fraud verification system. "
        "No claim is made regarding document authenticity or person identity."
    )
    disclaimer_table = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[540])
    disclaimer_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#f87171")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(disclaimer_table)
    elements.append(Spacer(1, 12))

    # Executive Summary Table
    elements.append(Paragraph("Executive Summary", section_title))
    tot_fields = sum(analysis.summary.values())
    summary_data = [
        ["Total Documents", str(len(analysis.documents))],
        ["Supported Fields (Grounding + Checks Passed)", str(analysis.summary.get("Supported", 0))],
        ["Inconsistent Fields (Discrepancy / Mismatch)", str(analysis.summary.get("Inconsistent", 0))],
        ["Uncertain Fields (Same-source / Ambiguous)", str(analysis.summary.get("Uncertain", 0))],
        ["Unreadable / Missing Fields", str(analysis.summary.get("Unreadable", 0))],
    ]
    summary_table = Table(summary_data, colWidths=[340, 200])
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ])
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 14))

    # Cross-Document Findings
    if analysis.cross_document_findings:
        elements.append(Paragraph("Cross-Document Consistency Reconciliation", section_title))
        for finding in analysis.cross_document_findings:
            bg_color = "#f0fdf4" if finding.status.value == "Supported" else ("#fef2f2" if finding.status.value == "Inconsistent" else "#fefce8")
            border_color = "#86efac" if finding.status.value == "Supported" else ("#fca5a5" if finding.status.value == "Inconsistent" else "#fde047")
            card_data = [
                [
                    Paragraph(f"<b>Rule:</b> {finding.rule_name} | <b>Status:</b> {finding.status.value}", body_style)
                ],
                [
                    Paragraph(f"<b>Documents:</b> {finding.doc_name_a} &lt;-&gt; {finding.doc_name_b}", subtitle_style)
                ],
                [
                    Paragraph(f"<b>Traceable Explanation:</b> {finding.explanation}", body_style)
                ]
            ]
            f_table = Table(card_data, colWidths=[540])
            f_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ])
            )
            elements.append(f_table)
            elements.append(Spacer(1, 6))
        elements.append(Spacer(1, 10))

    # Per-Document Details
    elements.append(Paragraph("Per-Document Field Extraction & Verification Details", section_title))
    for doc_id, doc_res in analysis.documents.items():
        doc_header = f"<b>Document:</b> {doc_res.filename} (Type: {doc_res.doc_type.value.upper()}) | Pages: {doc_res.page_count}"
        elements.append(Paragraph(doc_header, ParagraphStyle("DocH", parent=body_style, fontSize=10, textColor=colors.HexColor("#0369a1"))))
        elements.append(Spacer(1, 4))

        # Table of fields
        field_rows = [["Field Name", "Extracted Value", "Status", "Status Reason"]]
        for fname, fobj in doc_res.fields.items():
            val_display = str(fobj.normalized_value if fobj.normalized_value is not None else (fobj.value or "—"))
            field_rows.append([
                fname,
                val_display[:28],
                fobj.status.value,
                (fobj.status_reason or "Verified")[:45],
            ])

        if len(field_rows) > 1:
            f_table = Table(field_rows, colWidths=[120, 110, 80, 230])
            f_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(f_table)
            elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
