"""Unit tests for document classification and layout-aware parsing."""

from backend.app.schemas.common import DocumentType, EvidenceToken, FieldStatus
from backend.app.extraction.layout_parser import (
    group_tokens_into_lines,
    classify_document,
    parse_payslip,
    parse_bank_statement,
    parse_invoice,
)


def test_token_grouping_into_lines():
    tokens = [
        EvidenceToken(text="Acme", page=1, bbox=[0.1, 0.1, 0.2, 0.12]),
        EvidenceToken(text="Corporation", page=1, bbox=[0.22, 0.1, 0.35, 0.12]),
        EvidenceToken(text="Invoice", page=1, bbox=[0.1, 0.2, 0.2, 0.22]),
        EvidenceToken(text="#1024", page=1, bbox=[0.22, 0.2, 0.3, 0.22]),
    ]
    lines = group_tokens_into_lines(tokens)
    assert len(lines) == 2
    assert lines[0].text == "Acme Corporation"
    assert lines[1].text == "Invoice #1024"


def test_document_classification():
    payslip_tokens = [
        EvidenceToken(text="Salary Slip for October 2023", page=1, bbox=[0.1, 0.1, 0.5, 0.12]),
        EvidenceToken(text="Basic Pay: 50,000.00 Gross Earnings: 75,000.00 Net Pay: 65,000.00", page=1, bbox=[0.1, 0.2, 0.8, 0.22]),
    ]
    lines = group_tokens_into_lines(payslip_tokens)
    doc_type = classify_document(lines)
    assert doc_type == DocumentType.PAYSLIP

    bank_tokens = [
        EvidenceToken(text="Account Statement - State Bank", page=1, bbox=[0.1, 0.1, 0.5, 0.12]),
        EvidenceToken(text="Opening Balance: 10,000.00 Closing Balance: 45,000.00", page=1, bbox=[0.1, 0.2, 0.8, 0.22]),
    ]
    lines = group_tokens_into_lines(bank_tokens)
    doc_type = classify_document(lines)
    assert doc_type == DocumentType.BANK_STATEMENT


def test_payslip_parsing():
    tokens = [
        EvidenceToken(text="Acme Technologies Inc.", page=1, bbox=[0.1, 0.05, 0.4, 0.08]),
        EvidenceToken(text="Employee Name: Rahul Sharma", page=1, bbox=[0.1, 0.1, 0.5, 0.13]),
        EvidenceToken(text="Employee ID: EMP-9042", page=1, bbox=[0.1, 0.15, 0.4, 0.18]),
        EvidenceToken(text="Pay Period: 01/03/2024 to 31/03/2024", page=1, bbox=[0.1, 0.2, 0.6, 0.23]),
        EvidenceToken(text="Payment Date: 31/03/2024", page=1, bbox=[0.1, 0.25, 0.4, 0.28]),
        EvidenceToken(text="Basic Salary: ₹ 60,000.00", page=1, bbox=[0.1, 0.3, 0.4, 0.33]),
        EvidenceToken(text="HRA Allowance: ₹ 20,000.00", page=1, bbox=[0.1, 0.35, 0.4, 0.38]),
        EvidenceToken(text="Gross Salary: ₹ 80,000.00", page=1, bbox=[0.1, 0.4, 0.4, 0.43]),
        EvidenceToken(text="PF Deduction: ₹ 5,000.00", page=1, bbox=[0.1, 0.45, 0.4, 0.48]),
        EvidenceToken(text="Net Salary: ₹ 75,000.00", page=1, bbox=[0.1, 0.5, 0.4, 0.53]),
    ]
    lines = group_tokens_into_lines(tokens)
    fields, data = parse_payslip(lines)

    assert fields["employee_name"].normalized_value == "Rahul Sharma"
    assert fields["employee_id"].normalized_value == "EMP-9042"
    assert fields["employer_name"].normalized_value == "Acme Technologies Inc."
    assert fields["payment_date"].normalized_value == "2024-03-31"
    assert fields["basic_salary"].normalized_value == 60000.0
    assert fields["gross_salary"].normalized_value == 80000.0
    assert fields["net_salary"].normalized_value == 75000.0


def test_invoice_parsing():
    tokens = [
        EvidenceToken(text="Cloud Solutions Ltd.", page=1, bbox=[0.1, 0.05, 0.4, 0.08]),
        EvidenceToken(text="Tax Invoice # INV-8821", page=1, bbox=[0.1, 0.1, 0.5, 0.13]),
        EvidenceToken(text="Invoice Date: 15-Jan-2024", page=1, bbox=[0.1, 0.15, 0.4, 0.18]),
        EvidenceToken(text="Cloud Server Hosting 2 150.00 300.00", page=1, bbox=[0.1, 0.25, 0.6, 0.28]),
        EvidenceToken(text="Subtotal: $ 300.00", page=1, bbox=[0.1, 0.35, 0.4, 0.38]),
        EvidenceToken(text="Tax: $ 30.00", page=1, bbox=[0.1, 0.4, 0.4, 0.43]),
        EvidenceToken(text="Total: $ 330.00", page=1, bbox=[0.1, 0.45, 0.4, 0.48]),
    ]
    lines = group_tokens_into_lines(tokens)
    fields, data = parse_invoice(lines)

    assert fields["invoice_number"].normalized_value == "INV-8821"
    assert fields["invoice_date"].normalized_value == "2024-01-15"
    assert fields["subtotal"].normalized_value == 300.0
    assert fields["tax"].normalized_value == 30.0
    assert fields["total"].normalized_value == 330.0
    assert len(data.line_items) == 1
    assert data.line_items[0].quantity == 2.0
    assert data.line_items[0].unit_price == 150.0
    assert data.line_items[0].line_total == 300.0
