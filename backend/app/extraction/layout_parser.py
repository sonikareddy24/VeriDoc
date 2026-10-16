"""Layout-aware document parser and classifier.
Reconstructs horizontal text lines and spatial columns from evidence tokens,
classifies document type, and parses structured fields with label proximity and regexes.
Tuned strictly on development layouts.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from rapidfuzz import fuzz

from backend.app.schemas.common import (
    DocumentType,
    EvidenceToken,
    ExtractedField,
    FieldStatus,
    NullReason,
)
from backend.app.schemas.payslip import PayslipData, PayslipItem
from backend.app.schemas.bank_statement import BankStatementData, BankTransaction
from backend.app.schemas.invoice import InvoiceData, InvoiceLineItem
from backend.app.extraction.normalizers import normalize_amount, normalize_date


class TextLine:
    def __init__(self, tokens: List[EvidenceToken]):
        self.tokens = sorted(tokens, key=lambda t: t.bbox[0])
        self.text = " ".join(t.text for t in self.tokens)
        self.page = self.tokens[0].page
        self.y0 = min(t.bbox[1] for t in self.tokens)
        self.y1 = max(t.bbox[3] for t in self.tokens)
        self.x0 = min(t.bbox[0] for t in self.tokens)
        self.x1 = max(t.bbox[2] for t in self.tokens)
        self.avg_conf = sum(t.confidence or 0.8 for t in self.tokens) / len(self.tokens)

    @property
    def bbox(self) -> List[float]:
        return [round(self.x0, 4), round(self.y0, 4), round(self.x1, 4), round(self.y1, 4)]


def group_tokens_into_lines(tokens: List[EvidenceToken], y_threshold: float = 0.015) -> List[TextLine]:
    """Group tokens on the same page with close vertical centers into coherent lines."""
    if not tokens:
        return []

    # Sort primarily by page, then vertical center
    sorted_tokens = sorted(tokens, key=lambda t: (t.page, (t.bbox[1] + t.bbox[3]) / 2))
    lines: List[TextLine] = []
    current_group: List[EvidenceToken] = []
    current_page = None
    current_y_center = None

    for t in sorted_tokens:
        y_center = (t.bbox[1] + t.bbox[3]) / 2
        if not current_group:
            current_group.append(t)
            current_page = t.page
            current_y_center = y_center
        elif t.page == current_page and abs(y_center - current_y_center) < y_threshold:
            current_group.append(t)
            # Update running vertical center
            current_y_center = sum((item.bbox[1] + item.bbox[3]) / 2 for item in current_group) / len(current_group)
        else:
            lines.append(TextLine(current_group))
            current_group = [t]
            current_page = t.page
            current_y_center = y_center

    if current_group:
        lines.append(TextLine(current_group))

    return lines


def classify_document(lines: List[TextLine]) -> DocumentType:
    """Classifies document type based on key semantic markers."""
    full_text = " ".join(line.text.lower() for line in lines)

    payslip_score = sum(
        1 for term in ["payslip", "salary slip", "earnings", "deductions", "basic pay", "net pay", "employee id", "provident fund"]
        if term in full_text
    )
    bank_score = sum(
        1 for term in ["bank statement", "account statement", "opening balance", "closing balance", "withdrawal", "deposit", "running balance", "transaction date"]
        if term in full_text
    )
    invoice_score = sum(
        1 for term in ["tax invoice", "invoice #", "bill to", "due date", "subtotal", "gstin", "total amount", "line total"]
        if term in full_text
    )
    receipt_score = sum(
        1 for term in ["receipt", "cash receipt", "merchant", "store", "cashier"]
        if term in full_text
    )

    scores = {
        DocumentType.PAYSLIP: payslip_score,
        DocumentType.BANK_STATEMENT: bank_score,
        DocumentType.INVOICE: invoice_score,
        DocumentType.RECEIPT: receipt_score,
    }

    best_type, best_score = max(scores.items(), key=lambda x: x[1])
    if best_score >= 2:
        return best_type
    return DocumentType.UNKNOWN


def parse_payslip(lines: List[TextLine]) -> Tuple[Dict[str, ExtractedField], PayslipData]:
    """Parse payslip lines into typed ExtractedField objects and structured data."""
    fields: Dict[str, ExtractedField] = {}
    structured = PayslipData()

    allowances_list: List[PayslipItem] = []
    deductions_list: List[PayslipItem] = []

    # Patterns
    re_emp_name = re.compile(r"(?:employee\s+name|emp\s+name|name)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_emp_id = re.compile(r"(?:employee\s+id|emp\s+id|staff\s+no)\s*[:\-]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)
    re_employer = re.compile(r"(?:employer|company|organisation|organization)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_pay_period = re.compile(r"(?:pay\s+period|period|salary\s+month)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_pay_date = re.compile(r"(?:payment\s+date|pay\s+date|date\s+of\s+payment|disbursement\s+date)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_basic = re.compile(r"(?:basic\s+salary|basic\s+pay|basic)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)
    re_gross = re.compile(r"(?:gross\s+salary|gross\s+earnings|gross\s+pay|total\s+earnings)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)
    re_net = re.compile(r"(?:net\s+salary|net\s+pay|take\s+home|total\s+net\s+payable)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)

    # First pass: check top lines for employer if not explicitly labeled
    if lines and not structured.employer_name:
        for line in lines[:3]:
            # If line is bold header-like (short, no numbers, not "payslip")
            if not any(char.isdigit() for char in line.text) and "payslip" not in line.text.lower() and len(line.text) > 3:
                employer_field = ExtractedField(
                    name="employer_name",
                    value=line.text.strip(),
                    normalized_value=line.text.strip(),
                    status=FieldStatus.UNCERTAIN,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=line.text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["employer_name"] = employer_field
                structured.employer_name = employer_field
                break

    for line in lines:
        text = line.text

        # Employee Name
        if not structured.employee_name:
            m = re_emp_name.search(text)
            if m:
                raw_val = m.group(1).split("  ")[0].strip()
                field = ExtractedField(
                    name="employee_name",
                    value=raw_val,
                    normalized_value=raw_val.title(),
                    status=FieldStatus.UNCERTAIN,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["employee_name"] = field
                structured.employee_name = field

        # Employee ID
        if not structured.employee_id:
            m = re_emp_id.search(text)
            if m:
                raw_val = m.group(1).strip()
                field = ExtractedField(
                    name="employee_id",
                    value=raw_val,
                    normalized_value=raw_val.upper(),
                    status=FieldStatus.UNCERTAIN,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["employee_id"] = field
                structured.employee_id = field

        # Employer Name (if labeled)
        m_emp = re_employer.search(text)
        if m_emp:
            raw_val = m_emp.group(1).strip()
            field = ExtractedField(
                name="employer_name",
                value=raw_val,
                normalized_value=raw_val,
                status=FieldStatus.UNCERTAIN,
                page=line.page,
                bbox=line.bbox,
                source_text=text,
                ocr_confidence=round(line.avg_conf, 2),
            )
            fields["employer_name"] = field
            structured.employer_name = field

        # Payment Date
        if not structured.payment_date:
            m = re_pay_date.search(text)
            if m:
                raw_val = m.group(1).strip()
                iso_dt, snippet, amb = normalize_date(raw_val)
                field = ExtractedField(
                    name="payment_date",
                    value=raw_val,
                    normalized_value=iso_dt,
                    status=FieldStatus.UNCERTAIN,
                    status_reason="ambiguous_day_month" if amb else None,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["payment_date"] = field
                structured.payment_date = field

        # Pay Period
        if not structured.pay_period_start:
            m = re_pay_period.search(text)
            if m:
                raw_val = m.group(1).strip()
                # Check for range: "01/01/2024 to 31/01/2024" or "01-Jan-2024 - 31-Jan-2024"
                parts = re.split(r"\s+(?:to|-|until)\s+", raw_val, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    dt_start, _, _ = normalize_date(parts[0])
                    dt_end, _, _ = normalize_date(parts[1])
                    if dt_start:
                        f_start = ExtractedField(
                            name="pay_period_start",
                            value=parts[0].strip(),
                            normalized_value=dt_start,
                            status=FieldStatus.UNCERTAIN,
                            page=line.page,
                            bbox=line.bbox,
                            source_text=text,
                            ocr_confidence=round(line.avg_conf, 2),
                        )
                        fields["pay_period_start"] = f_start
                        structured.pay_period_start = f_start
                    if dt_end:
                        f_end = ExtractedField(
                            name="pay_period_end",
                            value=parts[1].strip(),
                            normalized_value=dt_end,
                            status=FieldStatus.UNCERTAIN,
                            page=line.page,
                            bbox=line.bbox,
                            source_text=text,
                            ocr_confidence=round(line.avg_conf, 2),
                        )
                        fields["pay_period_end"] = f_end
                        structured.pay_period_end = f_end
                else:
                    # Single date or month text like "March 2024"
                    dt, _, _ = normalize_date(raw_val)
                    if dt:
                        f_start = ExtractedField(
                            name="pay_period_start",
                            value=raw_val,
                            normalized_value=dt,
                            status=FieldStatus.UNCERTAIN,
                            page=line.page,
                            bbox=line.bbox,
                            source_text=text,
                            ocr_confidence=round(line.avg_conf, 2),
                        )
                        fields["pay_period_start"] = f_start
                        structured.pay_period_start = f_start

        # Basic Salary
        if not structured.basic_salary:
            m = re_basic.search(text)
            if m and "total" not in text.lower() and "gross" not in text.lower():
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="basic_salary",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["basic_salary"] = field
                    structured.basic_salary = field
                    if cur and not structured.currency:
                        f_cur = ExtractedField(
                            name="currency", value=cur, normalized_value=cur, status=FieldStatus.UNCERTAIN, page=line.page
                        )
                        fields["currency"] = f_cur
                        structured.currency = f_cur

        # Gross Salary
        if not structured.gross_salary:
            m = re_gross.search(text)
            if m:
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="gross_salary",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["gross_salary"] = field
                    structured.gross_salary = field

        # Net Salary
        if not structured.net_salary:
            m = re_net.search(text)
            if m:
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="net_salary",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["net_salary"] = field
                    structured.net_salary = field

        # Detect itemized allowances and deductions (e.g. HRA, Medical, PF, TDS)
        for allow_term in ["hra", "house rent", "conveyance", "special allowance", "medical allowance", "dearness allowance"]:
            if allow_term in text.lower() and "total" not in text.lower():
                val, cur, _ = normalize_amount(text)
                if val and val > 0:
                    allowances_list.append(PayslipItem(description=allow_term.upper(), amount=val))
                    break

        for ded_term in ["provident fund", "pf", "tds", "income tax", "professional tax", "insurance", "esi"]:
            if ded_term in text.lower() and "total" not in text.lower():
                val, cur, _ = normalize_amount(text)
                if val and val > 0:
                    deductions_list.append(PayslipItem(description=ded_term.upper(), amount=val))
                    break

    # Itemized totals
    if allowances_list:
        structured.allowances = allowances_list
        tot_allow = sum(item.amount for item in allowances_list)
        f_tot_allow = ExtractedField(
            name="total_allowances",
            value=f"{tot_allow:.2f}",
            normalized_value=round(tot_allow, 2),
            status=FieldStatus.UNCERTAIN,
        )
        fields["total_allowances"] = f_tot_allow
        structured.total_allowances = f_tot_allow

    if deductions_list:
        structured.deductions = deductions_list
        tot_ded = sum(item.amount for item in deductions_list)
        f_tot_ded = ExtractedField(
            name="total_deductions",
            value=f"{tot_ded:.2f}",
            normalized_value=round(tot_ded, 2),
            status=FieldStatus.UNCERTAIN,
        )
        fields["total_deductions"] = f_tot_ded
        structured.total_deductions = f_tot_ded

    # Ensure required fields have at least null entries with null_reason if missing
    for req_field in ["employee_name", "employee_id", "employer_name", "payment_date", "basic_salary", "gross_salary", "net_salary"]:
        if req_field not in fields:
            fields[req_field] = ExtractedField(
                name=req_field,
                value=None,
                normalized_value=None,
                status=FieldStatus.UNREADABLE,
                null_reason=NullReason.NOT_FOUND,
                status_reason=f"Field '{req_field}' was not detected in document text.",
            )

    return fields, structured


def parse_bank_statement(lines: List[TextLine]) -> Tuple[Dict[str, ExtractedField], BankStatementData]:
    """Parse bank statement header fields and table transactions."""
    fields: Dict[str, ExtractedField] = {}
    structured = BankStatementData()
    transactions: List[BankTransaction] = []

    re_holder = re.compile(r"(?:account\s+holder|name|customer\s+name|a/c\s+name)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_period = re.compile(r"(?:statement\s+period|period|from)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_open = re.compile(r"(?:opening\s+balance|opening\s+bal|start\s+balance)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)
    re_close = re.compile(r"(?:closing\s+balance|closing\s+bal|end\s+balance)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)

    row_counter = 0

    for line in lines:
        text = line.text

        # Account Holder
        if not structured.account_holder_name:
            m = re_holder.search(text)
            if m:
                raw_val = m.group(1).split("  ")[0].strip()
                field = ExtractedField(
                    name="account_holder_name",
                    value=raw_val,
                    normalized_value=raw_val.title(),
                    status=FieldStatus.UNCERTAIN,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["account_holder_name"] = field
                structured.account_holder_name = field

        # Statement Period
        if not structured.statement_period_start:
            m = re_period.search(text)
            if m:
                raw_val = m.group(1).strip()
                parts = re.split(r"\s+(?:to|-|until)\s+", raw_val, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    dt1, _, _ = normalize_date(parts[0])
                    dt2, _, _ = normalize_date(parts[1])
                    if dt1:
                        f_start = ExtractedField(
                            name="statement_period_start",
                            value=parts[0].strip(),
                            normalized_value=dt1,
                            status=FieldStatus.UNCERTAIN,
                            page=line.page,
                            bbox=line.bbox,
                            source_text=text,
                            ocr_confidence=round(line.avg_conf, 2),
                        )
                        fields["statement_period_start"] = f_start
                        structured.statement_period_start = f_start
                    if dt2:
                        f_end = ExtractedField(
                            name="statement_period_end",
                            value=parts[1].strip(),
                            normalized_value=dt2,
                            status=FieldStatus.UNCERTAIN,
                            page=line.page,
                            bbox=line.bbox,
                            source_text=text,
                            ocr_confidence=round(line.avg_conf, 2),
                        )
                        fields["statement_period_end"] = f_end
                        structured.statement_period_end = f_end

        # Opening Balance
        if not structured.opening_balance:
            m = re_open.search(text)
            if m:
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="opening_balance",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["opening_balance"] = field
                    structured.opening_balance = field
                    if cur and not structured.currency:
                        f_cur = ExtractedField(name="currency", value=cur, normalized_value=cur, status=FieldStatus.UNCERTAIN, page=line.page)
                        fields["currency"] = f_cur
                        structured.currency = f_cur

        # Closing Balance
        if not structured.closing_balance:
            m = re_close.search(text)
            if m:
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="closing_balance",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["closing_balance"] = field
                    structured.closing_balance = field

        # Transaction row extraction: look for date at line start or within line + amounts
        # e.g. "05/01/2024 Salary Credit - Acme Corp 75,000.00 1,25,000.00"
        iso_dt, dt_snippet, amb = normalize_date(text)
        if iso_dt and ("balance" not in text.lower() or "opening" not in text.lower()):
            # Find all numeric amount strings in this line
            amt_matches = list(re.finditer(r"[\d,]+\.\d{2}", text))
            if len(amt_matches) >= 1:
                row_counter += 1
                amounts = []
                for am in amt_matches:
                    v, _, _ = normalize_amount(am.group(0))
                    if v is not None:
                        amounts.append(v)

                # Determine debit/credit/balance
                debit: Optional[float] = None
                credit: Optional[float] = None
                balance: Optional[float] = None

                if len(amounts) == 1:
                    # Single amount: could be transaction or balance
                    balance = amounts[0]
                elif len(amounts) == 2:
                    # [tx_amount, running_balance]
                    tx_amt = amounts[0]
                    balance = amounts[1]
                    # Check keywords in text
                    if any(w in text.lower() for w in ["salary", "credit", "deposit", "cr"]):
                        credit = tx_amt
                    else:
                        debit = tx_amt
                elif len(amounts) >= 3:
                    # [debit, credit, balance] or [amt1, amt2, balance]
                    debit = amounts[0] if "dr" in text.lower() or amounts[0] > 0 else None
                    credit = amounts[1] if "cr" in text.lower() or amounts[1] > 0 else None
                    balance = amounts[-1]

                # Extract description
                # Strip date snippet and amounts from text
                desc = text
                if dt_snippet:
                    desc = desc.replace(dt_snippet, "")
                for am in amt_matches:
                    desc = desc.replace(am.group(0), "")
                desc = re.sub(r"[^\w\s\-\.]", "", desc).strip()

                transactions.append(
                    BankTransaction(
                        row_idx=row_counter,
                        date=iso_dt,
                        description=desc,
                        debit=debit,
                        credit=credit,
                        running_balance=balance,
                        raw_text=text,
                    )
                )

    structured.transactions = transactions

    for req_field in ["account_holder_name", "statement_period_start", "statement_period_end", "opening_balance", "closing_balance"]:
        if req_field not in fields:
            fields[req_field] = ExtractedField(
                name=req_field,
                value=None,
                normalized_value=None,
                status=FieldStatus.UNREADABLE,
                null_reason=NullReason.NOT_FOUND,
                status_reason=f"Field '{req_field}' was not detected in document text.",
            )

    return fields, structured


def parse_invoice(lines: List[TextLine]) -> Tuple[Dict[str, ExtractedField], InvoiceData]:
    """Parse invoice header fields, line items, and financial totals."""
    fields: Dict[str, ExtractedField] = {}
    structured = InvoiceData()
    line_items: List[InvoiceLineItem] = []

    re_merchant = re.compile(r"(?:merchant|vendor|seller|company|from)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_inv_no = re.compile(r"(?:invoice\s*(?:no|number|#)|inv\s*#|bill\s*#)\s*[:\-]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)
    re_date = re.compile(r"(?:invoice\s+date|date|billing\s+date)\s*[:\-]?\s*(.+)", re.IGNORECASE)
    re_subtotal = re.compile(r"(?:subtotal|sub\s+total|net\s+amount)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)
    re_tax = re.compile(r"(?:tax|vat|gst|sales\s+tax)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)
    re_discount = re.compile(r"(?:discount|rebate)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)
    re_total = re.compile(r"(?:grand\s+total|total\s+amount|total\s+due|total)\s*[:\-]?\s*([^\n]+)", re.IGNORECASE)

    # First line fallback for merchant if no explicit label
    if lines and not structured.merchant_name:
        for line in lines[:3]:
            if not any(char.isdigit() for char in line.text) and "invoice" not in line.text.lower() and len(line.text) > 3:
                field = ExtractedField(
                    name="merchant_name",
                    value=line.text.strip(),
                    normalized_value=line.text.strip(),
                    status=FieldStatus.UNCERTAIN,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=line.text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["merchant_name"] = field
                structured.merchant_name = field
                break

    for line in lines:
        text = line.text

        # Merchant Name (explicit)
        m = re_merchant.search(text)
        if m:
            raw_val = m.group(1).split("  ")[0].strip()
            field = ExtractedField(
                name="merchant_name",
                value=raw_val,
                normalized_value=raw_val,
                status=FieldStatus.UNCERTAIN,
                page=line.page,
                bbox=line.bbox,
                source_text=text,
                ocr_confidence=round(line.avg_conf, 2),
            )
            fields["merchant_name"] = field
            structured.merchant_name = field

        # Invoice Number
        if not structured.invoice_number:
            m = re_inv_no.search(text)
            if m:
                raw_val = m.group(1).strip()
                field = ExtractedField(
                    name="invoice_number",
                    value=raw_val,
                    normalized_value=raw_val.upper(),
                    status=FieldStatus.UNCERTAIN,
                    page=line.page,
                    bbox=line.bbox,
                    source_text=text,
                    ocr_confidence=round(line.avg_conf, 2),
                )
                fields["invoice_number"] = field
                structured.invoice_number = field

        # Invoice Date
        if not structured.invoice_date:
            m = re_date.search(text)
            if m and "due" not in text.lower():
                raw_val = m.group(1).strip()
                iso_dt, snippet, amb = normalize_date(raw_val)
                if iso_dt:
                    field = ExtractedField(
                        name="invoice_date",
                        value=raw_val,
                        normalized_value=iso_dt,
                        status=FieldStatus.UNCERTAIN,
                        status_reason="ambiguous_day_month" if amb else None,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["invoice_date"] = field
                    structured.invoice_date = field

        # Subtotal
        if not structured.subtotal:
            m = re_subtotal.search(text)
            if m:
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="subtotal",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["subtotal"] = field
                    structured.subtotal = field
                    if cur and not structured.currency:
                        f_cur = ExtractedField(name="currency", value=cur, normalized_value=cur, status=FieldStatus.UNCERTAIN, page=line.page)
                        fields["currency"] = f_cur
                        structured.currency = f_cur

        # Tax
        if not structured.tax:
            m = re_tax.search(text)
            if m and "rate" not in text.lower() and "invoice" not in text.lower():
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="tax",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["tax"] = field
                    structured.tax = field

        # Discounts
        if not structured.discounts:
            m = re_discount.search(text)
            if m:
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="discounts",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["discounts"] = field
                    structured.discounts = field

        # Total
        if not structured.total:
            m = re_total.search(text)
            if m and "sub" not in text.lower():
                val, cur, _ = normalize_amount(m.group(1))
                if val is not None:
                    field = ExtractedField(
                        name="total",
                        value=m.group(1).strip(),
                        normalized_value=val,
                        status=FieldStatus.UNCERTAIN,
                        page=line.page,
                        bbox=line.bbox,
                        source_text=text,
                        ocr_confidence=round(line.avg_conf, 2),
                    )
                    fields["total"] = field
                    structured.total = field

        # Line items: table rows like: "Cloud Server Hosting 2 120.00 240.00"
        # Look for description followed by 2 or 3 numbers (quantity, price, line_total)
        num_matches = list(re.finditer(r"[\d,]+(?:\.\d{2})?", text))
        if len(num_matches) >= 2 and not any(k in text.lower() for k in ["total", "subtotal", "tax", "vat", "gst", "invoice"]):
            try:
                # Last number is total, second to last is unit price, third to last is qty (if exists)
                total_val, _, _ = normalize_amount(num_matches[-1].group(0))
                price_val, _, _ = normalize_amount(num_matches[-2].group(0))
                qty_val = 1.0
                if len(num_matches) >= 3:
                    q, _, _ = normalize_amount(num_matches[-3].group(0))
                    if q and 0 < q < 10000:
                        qty_val = q

                if total_val and price_val and total_val > 0 and price_val > 0:
                    desc = text[:num_matches[0].start()].strip()
                    if len(desc) >= 3:
                        line_items.append(
                            InvoiceLineItem(
                                description=desc,
                                quantity=qty_val,
                                unit_price=price_val,
                                line_total=total_val,
                            )
                        )
            except Exception:
                pass

    structured.line_items = line_items

    for req_field in ["merchant_name", "invoice_number", "invoice_date", "subtotal", "total"]:
        if req_field not in fields:
            fields[req_field] = ExtractedField(
                name=req_field,
                value=None,
                normalized_value=None,
                status=FieldStatus.UNREADABLE,
                null_reason=NullReason.NOT_FOUND,
                status_reason=f"Field '{req_field}' was not detected in document text.",
            )

    return fields, structured
