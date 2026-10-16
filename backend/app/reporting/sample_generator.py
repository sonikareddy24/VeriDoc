"""Generates realistic synthetic demonstration documents (PDFs) for the demo flow.
Creates a valid payslip and matching bank statement with clean formatting.
"""

import io
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def create_demo_payslip() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("<b>INFOSYS GLOBAL TECHNOLOGIES LTD.</b>", ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, leading=20)),
        Paragraph("Electronics City, Hosur Road, Bangalore, Karnataka - 560100", ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, textColor=colors.gray)),
        Spacer(1, 10),
        Paragraph("<b>PAYSLIP FOR THE MONTH OF MARCH 2024</b>", ParagraphStyle("Title", parent=styles["Heading2"], fontSize=12, leading=16)),
        Spacer(1, 10),
    ]

    emp_meta = [
        ["Employee Name:", "Amit Verma", "Employee ID:", "INF-84920"],
        ["Pay Period:", "01/03/2024 to 31/03/2024", "Payment Date:", "31/03/2024"],
        ["Bank Account:", "HDFC Bank - ****4109", "PAN / Tax ID:", "ABCDE1234F"],
    ]
    t_meta = Table(emp_meta, colWidths=[100, 160, 100, 160])
    t_meta.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))

    # Earnings & Deductions
    salary_breakdown = [
        ["Earnings", "Amount (INR)", "Deductions", "Amount (INR)"],
        ["Basic Salary", "50,000.00", "Provident Fund (PF)", "3,600.00"],
        ["House Rent Allowance (HRA)", "20,000.00", "Professional Tax", "200.00"],
        ["Special Allowance", "15,000.00", "Income Tax (TDS)", "6,200.00"],
        ["Gross Salary", "85,000.00", "Total Deductions", "10,000.00"],
        ["", "", "Net Salary Payable", "75,000.00"],
    ]
    t_sal = Table(salary_breakdown, colWidths=[150, 110, 150, 110])
    t_sal.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 4), (-1, 5), "Helvetica-Bold"),
        ("BACKGROUND", (2, 5), (3, 5), colors.HexColor("#f0fdf4")),
        ("TEXTCOLOR", (2, 5), (3, 5), colors.HexColor("#166534")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_sal)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def create_demo_bank_statement() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("<b>HDFC BANK LTD. - ACCOUNT STATEMENT</b>", ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, leading=20)),
        Paragraph("Bangalore Koramangala Branch | IFSC: HDFC0000128", ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, textColor=colors.gray)),
        Spacer(1, 10),
    ]

    holder_meta = [
        ["Account Holder:", "Amit Verma", "Account Number:", "501002394109"],
        ["Statement Period:", "01/03/2024 to 05/04/2024", "Currency:", "INR"],
        ["Opening Balance:", "₹ 25,400.00", "Closing Balance:", "₹ 91,200.00"],
    ]
    t_holder = Table(holder_meta, colWidths=[110, 160, 110, 140])
    t_holder.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_holder)
    elements.append(Spacer(1, 15))

    tx_data = [
        ["Date", "Description", "Debit", "Credit", "Balance"],
        ["05/03/2024", "ATM Cash Withdrawal", "5,000.00", "-", "20,400.00"],
        ["12/03/2024", "Grocery Mart UPI", "4,200.00", "-", "16,200.00"],
        ["31/03/2024", "Salary Credit - Infosys Ltd", "-", "75,000.00", "91,200.00"],
    ]
    t_tx = Table(tx_data, colWidths=[75, 205, 80, 80, 80])
    t_tx.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_tx)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
