"""Central Verification Engine orchestrating grounding, deterministic arithmetic,
continuity, security hygiene, and multi-status aggregation.
"""

from typing import Dict, List, Optional
from backend.app.schemas.common import (
    DocumentType,
    EvidenceIndependence,
    ExtractedField,
    FieldStatus,
    ReviewCategory,
    VerificationCheck,
)
from backend.app.schemas.document import DocumentAnalysisResult
from backend.app.verification.grounding import verify_evidence_grounding
from backend.app.verification.format_plausibility import verify_format_and_plausibility
from backend.app.verification.payslip_arithmetic import verify_payslip_arithmetic
from backend.app.verification.invoice_arithmetic import verify_invoice_arithmetic
from backend.app.verification.bank_continuity import verify_bank_statement_continuity
from backend.app.verification.injection_hygiene import check_prompt_injection_hygiene


class VerificationEngine:
    def verify_document(self, result: DocumentAnalysisResult) -> DocumentAnalysisResult:
        """Applies all deterministic verification checks and updates field statuses and review categories."""
        all_checks: List[VerificationCheck] = []
        tokens = result.evidence_tokens
        fields = result.fields
        doc_type = result.doc_type
        structured = result.structured_data

        # 1. Evidence Grounding for each extracted field
        grounding_checks: Dict[str, VerificationCheck] = {}
        for f_name, field in fields.items():
            if field.value is not None or field.normalized_value is not None:
                g_check = verify_evidence_grounding(f_name, field, tokens)
                grounding_checks[f_name] = g_check
                all_checks.append(g_check)

        # 2. Format and Plausibility Checks
        fp_checks = verify_format_and_plausibility(doc_type.value, fields)
        all_checks.extend(fp_checks)

        # 3. Domain-Specific Deterministic Checks
        if doc_type == DocumentType.PAYSLIP:
            p_checks = verify_payslip_arithmetic(fields, structured)
            all_checks.extend(p_checks)
        elif doc_type in (DocumentType.INVOICE, DocumentType.RECEIPT):
            i_checks = verify_invoice_arithmetic(fields, structured)
            all_checks.extend(i_checks)
        elif doc_type == DocumentType.BANK_STATEMENT:
            b_checks = verify_bank_statement_continuity(fields, structured)
            all_checks.extend(b_checks)

        # 4. Security / Injection Hygiene Check
        sec_checks = check_prompt_injection_hygiene(tokens)
        all_checks.extend(sec_checks)

        # 5. Field Status Resolution
        # Look for checks that failed
        failed_checks = [c for c in all_checks if c.status == "failed"]
        failed_check_ids = {c.check_id for c in failed_checks}

        for f_name, field in fields.items():
            # If already marked unreadable, keep it
            if field.status == FieldStatus.UNREADABLE or field.value is None:
                field.status = FieldStatus.UNREADABLE
                continue

            g_check = grounding_checks.get(f_name)

            # Check if this specific field failed any check
            field_failed = False
            for fc in failed_checks:
                if f_name.upper() in fc.check_id or f"PLAUSIBILITY_NON_NEGATIVE_{f_name.upper()}" == fc.check_id:
                    field_failed = True
                    break

            if field_failed or (g_check and g_check.status == "failed"):
                field.status = FieldStatus.INCONSISTENT
                field.status_reason = "Contradicted by deterministic check or absent from document evidence."
            elif g_check and g_check.independence == EvidenceIndependence.SAME_SOURCE:
                # Same-source evidence cannot self-certify as Supported
                field.status = FieldStatus.UNCERTAIN
                field.status_reason = "Grounded by same-source OCR engine only (insufficient independent confirmation)."
            elif g_check and g_check.status == "passed":
                # Check domain arithmetic failures: if domain arithmetic failed, related fields become Inconsistent
                arithmetic_failed = any(
                    c.status == "failed" for c in all_checks
                    if c.check_id in ["PAYSLIP_GROSS_ARITHMETIC", "PAYSLIP_NET_ARITHMETIC", "INVOICE_TOTAL_CALCULATION", "INVOICE_LINE_ITEMS_SUM"]
                )
                if arithmetic_failed and f_name in ["gross_salary", "net_salary", "subtotal", "total", "tax"]:
                    field.status = FieldStatus.INCONSISTENT
                    field.status_reason = "Arithmetic mismatch detected among related financial totals."
                else:
                    field.status = FieldStatus.SUPPORTED
                    field.status_reason = "Grounded in independent evidence and passed all applicable deterministic checks."
            else:
                field.status = FieldStatus.UNCERTAIN

        # 6. Assign Document-Level Review Categories (Never "fraud")
        review_categories: List[ReviewCategory] = []

        if result.quality.is_blurry or len(result.quality.warnings) > 0:
            review_categories.append(ReviewCategory.IMAGE_QUALITY_PROBLEM)

        if any(f.status == FieldStatus.UNREADABLE for f in fields.values()):
            review_categories.append(ReviewCategory.EXTRACTION_ERROR_LIKELY)

        if failed_checks or any(f.status == FieldStatus.INCONSISTENT for f in fields.values()):
            review_categories.append(ReviewCategory.CONSISTENCY_ISSUE_NEEDS_REVIEW)

        # 7. Update Field Status Summary Counts
        counts = {
            FieldStatus.SUPPORTED.value: sum(1 for f in fields.values() if f.status == FieldStatus.SUPPORTED),
            FieldStatus.INCONSISTENT.value: sum(1 for f in fields.values() if f.status == FieldStatus.INCONSISTENT),
            FieldStatus.UNCERTAIN.value: sum(1 for f in fields.values() if f.status == FieldStatus.UNCERTAIN),
            FieldStatus.UNREADABLE.value: sum(1 for f in fields.values() if f.status == FieldStatus.UNREADABLE),
        }

        result.checks = all_checks
        result.review_categories = review_categories
        result.field_counts = counts
        return result


verification_engine = VerificationEngine()
