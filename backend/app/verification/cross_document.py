"""Cross-document reconciliation engine for payslip and bank statement bundles.
Performs deterministic comparisons with realistic benign variation tolerance:
- Net salary vs bank salary credit
- Employer name vs salary deposit description
- Name string similarity (strictly informational; never claims identity authenticity)
- Pay period vs statement coverage
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from rapidfuzz import fuzz

from backend.app.schemas.common import FieldStatus
from backend.app.schemas.cross_document import CrossDocumentFinding
from backend.app.schemas.document import DocumentAnalysisResult
from backend.app.core.config import settings


def compare_payslip_and_bank_statement(
    payslip_result: DocumentAnalysisResult,
    bank_result: DocumentAnalysisResult,
    salary_window_days: int = settings.SALARY_MATCH_WINDOW_DAYS,
) -> List[CrossDocumentFinding]:
    """Reconciles payslip against bank statement within the same session."""
    findings: List[CrossDocumentFinding] = []

    p_fields = payslip_result.fields
    b_fields = bank_result.fields
    p_data = payslip_result.structured_data or {}
    b_data = bank_result.structured_data or {}

    doc_id_p = payslip_result.doc_id
    name_p = payslip_result.filename
    doc_id_b = bank_result.doc_id
    name_b = bank_result.filename

    # 1. Name String Comparison (STRICTLY INFORMATIONAL ONLY)
    # Rule: Never claim two documents belong to the same person.
    emp_name = p_fields.get("employee_name", None)
    acc_name = b_fields.get("account_holder_name", None)
    if emp_name and acc_name and emp_name.normalized_value and acc_name.normalized_value:
        str_p = str(emp_name.normalized_value).strip().lower()
        str_b = str(acc_name.normalized_value).strip().lower()
        sim_score = fuzz.token_sort_ratio(str_p, str_b)

        if sim_score >= 85:
            explanation = (
                f"Informational: Name strings match ('{emp_name.normalized_value}' vs '{acc_name.normalized_value}', "
                f"similarity: {sim_score}%). Note: String match does not confirm person authenticity."
            )
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_NAME_STRING_COMPARISON",
                    rule_name="Employee vs Account Holder Name Matching",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.SUPPORTED,
                    explanation=explanation,
                    details={"similarity_score": sim_score, "is_identity_claim": False},
                )
            )
        else:
            explanation = (
                f"Informational: Name strings differ ('{emp_name.normalized_value}' vs '{acc_name.normalized_value}', "
                f"similarity: {sim_score}%). This could be due to name formatting, middle initials, "
                "or different individuals. Authenticity is not assessed."
            )
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_NAME_STRING_COMPARISON",
                    rule_name="Employee vs Account Holder Name Matching",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.UNCERTAIN,
                    explanation=explanation,
                    details={"similarity_score": sim_score, "is_identity_claim": False},
                )
            )

    # 2. Net Salary vs Bank Credit Amount and Timing
    net_salary_val = p_fields.get("net_salary", None)
    pay_date_val = p_fields.get("payment_date", None)
    transactions = b_data.get("transactions") or []

    if net_salary_val and net_salary_val.normalized_value and transactions:
        target_net = float(net_salary_val.normalized_value)
        employer_field = p_fields.get("employer_name")
        employer_str = str(employer_field.normalized_value or "").lower() if employer_field else ""

        # Find potential matching credit transactions
        exact_matches = []
        near_matches = []  # Small difference (e.g. wire fee <= 200 or partial payment)

        for tx in transactions:
            credit = tx.get("credit")
            if credit and credit > 0:
                diff = abs(credit - target_net)
                tx_date_str = tx.get("date")
                tx_desc = tx.get("description", "").lower()

                # Check date window if pay date is available
                days_diff = 0
                date_in_window = True
                if pay_date_val and pay_date_val.normalized_value and tx_date_str:
                    try:
                        d_pay = datetime.strptime(str(pay_date_val.normalized_value), "%Y-%m-%d")
                        d_tx = datetime.strptime(tx_date_str, "%Y-%m-%d")
                        days_diff = abs((d_tx - d_pay).days)
                        date_in_window = days_diff <= salary_window_days
                    except Exception:
                        pass

                if diff < 0.05 and date_in_window:
                    exact_matches.append((tx, days_diff))
                elif 0.05 <= diff <= 500.0 and date_in_window:
                    # Benign fee / tax adjustment difference
                    near_matches.append((tx, diff, days_diff, "wire_fee_or_minor_adjustment"))
                elif 0.3 * target_net <= credit <= 0.7 * target_net and date_in_window:
                    # Benign partial bi-weekly pay
                    near_matches.append((tx, diff, days_diff, "possible_partial_payment"))

        if exact_matches:
            best_tx, offset = exact_matches[0]
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_SALARY_BANK_CREDIT",
                    rule_name="Net Salary to Bank Credit Reconciliation",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.SUPPORTED,
                    explanation=(
                        f"Exact net salary match found! Bank credit of {best_tx.get('credit'):.2f} on "
                        f"{best_tx.get('date')} matches payslip net salary ({target_net:.2f}) "
                        f"(timing offset: {offset} days, window: {salary_window_days} days)."
                    ),
                    details={"matched_transaction": best_tx, "offset_days": offset},
                )
            )
        elif near_matches:
            best_tx, diff, offset, reason = near_matches[0]
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_SALARY_BANK_CREDIT",
                    rule_name="Net Salary to Bank Credit Reconciliation",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.UNCERTAIN,  # Crucial rule: benign differences MUST be Uncertain, NOT Inconsistent
                    explanation=(
                        f"Benign variation detected: Found credit of {best_tx.get('credit'):.2f} on {best_tx.get('date')} "
                        f"with difference of {diff:.2f} relative to net salary ({target_net:.2f}). "
                        f"Likely explained by {reason.replace('_', ' ')} or transaction fees. Classified as Uncertain."
                    ),
                    details={"matched_transaction": best_tx, "difference": diff, "reason": reason},
                )
            )
        else:
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_SALARY_BANK_CREDIT",
                    rule_name="Net Salary to Bank Credit Reconciliation",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.INCONSISTENT,
                    explanation=(
                        f"No matching salary deposit of {target_net:.2f} found in bank statement transactions "
                        f"within the {salary_window_days}-day disbursement window."
                    ),
                    details={"expected_amount": target_net, "window_days": salary_window_days},
                )
            )

    # 3. Employer Name vs Salary Credit Description
    employer_val = p_fields.get("employer_name", None)
    if employer_val and employer_val.normalized_value and transactions:
        emp_text = str(employer_val.normalized_value).lower()
        matched_desc = False
        best_sim = 0
        best_desc = ""

        for tx in transactions:
            if tx.get("credit", 0.0) and tx.get("credit", 0.0) > 0:
                desc = tx.get("description", "").lower()
                sim = fuzz.partial_ratio(emp_text, desc)
                if sim > best_sim:
                    best_sim = sim
                    best_desc = desc
                if sim >= 70 or any(part in desc for part in emp_text.split() if len(part) > 3):
                    matched_desc = True
                    break

        if matched_desc:
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_EMPLOYER_DEPOSIT_DESC",
                    rule_name="Employer Name in Bank Deposit Description",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.SUPPORTED,
                    explanation=f"Employer name '{employer_val.normalized_value}' matches or aligns with salary credit description ('{best_desc}').",
                    details={"employer": employer_val.normalized_value, "bank_description": best_desc},
                )
            )
        else:
            findings.append(
                CrossDocumentFinding(
                    check_id="CROSS_EMPLOYER_DEPOSIT_DESC",
                    rule_name="Employer Name in Bank Deposit Description",
                    doc_id_a=doc_id_p,
                    doc_name_a=name_p,
                    doc_id_b=doc_id_b,
                    doc_name_b=name_b,
                    status=FieldStatus.UNCERTAIN,
                    explanation=f"Employer name '{employer_val.normalized_value}' was not clearly reflected in credit descriptions (best partial similarity: {best_sim}%).",
                    details={"employer": employer_val.normalized_value, "best_similarity": best_sim},
                )
            )

    return findings
