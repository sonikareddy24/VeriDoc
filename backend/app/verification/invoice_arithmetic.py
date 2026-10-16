"""Deterministic arithmetic verification for Invoices and Receipts.
Checks:
1. sum(line item qty * unit_price) == subtotal
2. subtotal - discount + tax == total
3. Tax rate plausibility (0% <= rate <= 40%)
"""

from typing import Dict, List, Optional, Any
from backend.app.schemas.common import (
    EvidenceIndependence,
    ExtractedField,
    VerificationCheck,
)


def verify_invoice_arithmetic(
    fields: Dict[str, ExtractedField],
    structured_data: Optional[Dict[str, Any]] = None,
    tolerance: float = 0.05,
) -> List[VerificationCheck]:
    checks: List[VerificationCheck] = []

    subtotal_val = fields.get("subtotal", ExtractedField(name="subtotal")).normalized_value
    tax_val = fields.get("tax", ExtractedField(name="tax")).normalized_value or 0.0
    discount_val = fields.get("discounts", ExtractedField(name="discounts")).normalized_value or 0.0
    total_val = fields.get("total", ExtractedField(name="total")).normalized_value

    line_items = []
    if structured_data:
        line_items = structured_data.get("line_items") or []

    # 1. Line items sum vs Subtotal
    if line_items and subtotal_val is not None:
        computed_subtotal = sum(
            float(item.get("quantity", 1.0)) * float(item.get("unit_price", 0.0))
            for item in line_items
        )
        diff = abs(subtotal_val - computed_subtotal)
        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="INVOICE_LINE_ITEMS_SUM",
                    applies=True,
                    status="passed",
                    plain_explanation=(
                        f"Subtotal ({subtotal_val:.2f}) matches sum of line items "
                        f"({computed_subtotal:.2f}) within tolerance ({diff:.2f} <= {tolerance})."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="INVOICE_LINE_ITEMS_SUM",
                    applies=True,
                    status="failed",
                    plain_explanation=(
                        f"Line item calculation discrepancy: Stated subtotal ({subtotal_val:.2f}) "
                        f"does NOT match computed item sum ({computed_subtotal:.2f}). Difference: {diff:.2f}."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
    else:
        checks.append(
            VerificationCheck(
                check_id="INVOICE_LINE_ITEMS_SUM",
                applies=False,
                applies_reason="Missing line items or subtotal field.",
                status="indeterminate",
                plain_explanation="Skipped line item verification due to absent itemization.",
            )
        )

    # 2. Total calculation: subtotal - discount + tax == total
    if subtotal_val is not None and total_val is not None:
        expected_total = subtotal_val - discount_val + tax_val
        diff = abs(total_val - expected_total)
        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="INVOICE_TOTAL_CALCULATION",
                    applies=True,
                    status="passed",
                    plain_explanation=(
                        f"Grand total ({total_val:.2f}) matches subtotal ({subtotal_val:.2f}) - "
                        f"discount ({discount_val:.2f}) + tax ({tax_val:.2f}) within tolerance ({diff:.2f} <= {tolerance})."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="INVOICE_TOTAL_CALCULATION",
                    applies=True,
                    status="failed",
                    plain_explanation=(
                        f"Total calculation mismatch: Stated total ({total_val:.2f}) does NOT match "
                        f"subtotal ({subtotal_val:.2f}) - discount ({discount_val:.2f}) + tax ({tax_val:.2f}). "
                        f"Expected {expected_total:.2f}, difference is {diff:.2f}."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
    else:
        checks.append(
            VerificationCheck(
                check_id="INVOICE_TOTAL_CALCULATION",
                applies=False,
                applies_reason="Missing subtotal or grand total field.",
                status="indeterminate",
                plain_explanation="Skipped total calculation check due to missing fields.",
            )
        )

    # 3. Tax rate plausibility
    if subtotal_val is not None and subtotal_val > 0 and tax_val > 0:
        effective_rate = (tax_val / subtotal_val) * 100.0
        if 0.0 <= effective_rate <= 40.0:
            checks.append(
                VerificationCheck(
                    check_id="INVOICE_TAX_RATE_PLAUSIBILITY",
                    applies=True,
                    status="passed",
                    plain_explanation=f"Effective tax rate ({effective_rate:.1f}%) is within plausible range (0% - 40%).",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="INVOICE_TAX_RATE_PLAUSIBILITY",
                    applies=True,
                    status="failed",
                    plain_explanation=f"Effective tax rate ({effective_rate:.1f}%) is outside plausible range (0% - 40%).",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )

    return checks
