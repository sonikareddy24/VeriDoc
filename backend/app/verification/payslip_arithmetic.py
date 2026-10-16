"""Deterministic arithmetic verification for payslips.
Applies:
1. gross_salary == basic_salary + total_allowances
2. net_salary == gross_salary - total_deductions
3. total_allowances == sum(allowance items)
4. total_deductions == sum(deduction items)
"""

from typing import Dict, List, Optional, Any
from backend.app.schemas.common import (
    EvidenceIndependence,
    ExtractedField,
    VerificationCheck,
)


def verify_payslip_arithmetic(
    fields: Dict[str, ExtractedField],
    structured_data: Optional[Dict[str, Any]] = None,
    tolerance: float = 0.05,
) -> List[VerificationCheck]:
    checks: List[VerificationCheck] = []

    basic_val = fields.get("basic_salary", ExtractedField(name="basic")).normalized_value
    gross_val = fields.get("gross_salary", ExtractedField(name="gross")).normalized_value
    net_val = fields.get("net_salary", ExtractedField(name="net")).normalized_value
    allow_val = fields.get("total_allowances", ExtractedField(name="allow")).normalized_value
    ded_val = fields.get("total_deductions", ExtractedField(name="ded")).normalized_value

    # Extract itemized lists if present in structured_data
    allowance_items = []
    deduction_items = []
    if structured_data:
        allowance_items = structured_data.get("allowances") or []
        deduction_items = structured_data.get("deductions") or []

    # 1. Gross arithmetic check: gross == basic + allowances
    # If total_allowances is missing but items exist, compute sum
    effective_allowances = allow_val
    if effective_allowances is None and allowance_items:
        effective_allowances = sum(item.get("amount", 0.0) for item in allowance_items)
    elif effective_allowances is None and gross_val is not None and basic_val is not None and abs(gross_val - basic_val) < tolerance:
        # No allowances at all (gross == basic)
        effective_allowances = 0.0

    if gross_val is not None and basic_val is not None and effective_allowances is not None:
        expected_gross = basic_val + effective_allowances
        diff = abs(gross_val - expected_gross)
        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_GROSS_ARITHMETIC",
                    applies=True,
                    status="passed",
                    plain_explanation=(
                        f"Gross salary ({gross_val:.2f}) matches basic ({basic_val:.2f}) + "
                        f"allowances ({effective_allowances:.2f}) within tolerance ({diff:.2f} <= {tolerance})."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_GROSS_ARITHMETIC",
                    applies=True,
                    status="failed",
                    plain_explanation=(
                        f"Arithmetic mismatch: Gross salary ({gross_val:.2f}) does NOT equal "
                        f"basic ({basic_val:.2f}) + allowances ({effective_allowances:.2f}). "
                        f"Expected {expected_gross:.2f}, difference is {diff:.2f}."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
    else:
        missing = []
        if gross_val is None: missing.append("gross_salary")
        if basic_val is None: missing.append("basic_salary")
        if effective_allowances is None: missing.append("allowances")
        checks.append(
            VerificationCheck(
                check_id="PAYSLIP_GROSS_ARITHMETIC",
                applies=False,
                applies_reason=f"Cannot verify gross arithmetic because fields are missing: {', '.join(missing)}.",
                status="indeterminate",
                plain_explanation="Gross arithmetic check skipped due to missing component fields.",
            )
        )

    # 2. Net arithmetic check: net == gross - deductions
    effective_deductions = ded_val
    if effective_deductions is None and deduction_items:
        effective_deductions = sum(item.get("amount", 0.0) for item in deduction_items)
    elif effective_deductions is None and gross_val is not None and net_val is not None:
        effective_deductions = gross_val - net_val  # deduce if zero or single figure

    if net_val is not None and gross_val is not None and effective_deductions is not None:
        expected_net = gross_val - effective_deductions
        diff = abs(net_val - expected_net)
        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_NET_ARITHMETIC",
                    applies=True,
                    status="passed",
                    plain_explanation=(
                        f"Net salary ({net_val:.2f}) equals gross ({gross_val:.2f}) minus "
                        f"deductions ({effective_deductions:.2f}) within tolerance ({diff:.2f} <= {tolerance})."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_NET_ARITHMETIC",
                    applies=True,
                    status="failed",
                    plain_explanation=(
                        f"Arithmetic mismatch: Net salary ({net_val:.2f}) does NOT equal "
                        f"gross ({gross_val:.2f}) minus deductions ({effective_deductions:.2f}). "
                        f"Expected {expected_net:.2f}, difference is {diff:.2f}."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
    else:
        missing = []
        if net_val is None: missing.append("net_salary")
        if gross_val is None: missing.append("gross_salary")
        if effective_deductions is None: missing.append("deductions")
        checks.append(
            VerificationCheck(
                check_id="PAYSLIP_NET_ARITHMETIC",
                applies=False,
                applies_reason=f"Cannot verify net arithmetic because fields are missing: {', '.join(missing)}.",
                status="indeterminate",
                plain_explanation="Net arithmetic check skipped due to missing component fields.",
            )
        )

    # 3. Itemized allowances sum
    if allow_val is not None and allowance_items:
        item_sum = sum(item.get("amount", 0.0) for item in allowance_items)
        diff = abs(allow_val - item_sum)
        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_ALLOWANCES_ITEMIZED",
                    applies=True,
                    status="passed",
                    plain_explanation=f"Stated allowances total ({allow_val:.2f}) matches sum of line items ({item_sum:.2f}).",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_ALLOWANCES_ITEMIZED",
                    applies=True,
                    status="failed",
                    plain_explanation=f"Stated allowances total ({allow_val:.2f}) does NOT match sum of line items ({item_sum:.2f}).",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )

    # 4. Itemized deductions sum
    if ded_val is not None and deduction_items:
        item_sum = sum(item.get("amount", 0.0) for item in deduction_items)
        diff = abs(ded_val - item_sum)
        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_DEDUCTIONS_ITEMIZED",
                    applies=True,
                    status="passed",
                    plain_explanation=f"Stated deductions total ({ded_val:.2f}) matches sum of line items ({item_sum:.2f}).",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="PAYSLIP_DEDUCTIONS_ITEMIZED",
                    applies=True,
                    status="failed",
                    plain_explanation=f"Stated deductions total ({ded_val:.2f}) does NOT match sum of line items ({item_sum:.2f}).",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )

    return checks
