"""Format, plausibility, and range consistency checks."""

from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.common import (
    EvidenceIndependence,
    ExtractedField,
    VerificationCheck,
)


def verify_format_and_plausibility(
    doc_type: str,
    fields: Dict[str, ExtractedField],
) -> List[VerificationCheck]:
    checks: List[VerificationCheck] = []

    # 1. Non-negative amounts check
    non_negative_keys = [
        "basic_salary", "gross_salary", "net_salary",
        "opening_balance", "closing_balance",
        "subtotal", "total", "tax"
    ]
    for key in non_negative_keys:
        if key in fields and fields[key].normalized_value is not None:
            val = fields[key].normalized_value
            if isinstance(val, (int, float)):
                cid = f"PLAUSIBILITY_NON_NEGATIVE_{key.upper()}"
                if val < 0:
                    checks.append(
                        VerificationCheck(
                            check_id=cid,
                            applies=True,
                            status="failed",
                            plain_explanation=f"Field '{key}' has an impossible negative value ({val}).",
                            independence=EvidenceIndependence.INDEPENDENT,
                        )
                    )
                else:
                    checks.append(
                        VerificationCheck(
                            check_id=cid,
                            applies=True,
                            status="passed",
                            plain_explanation=f"Field '{key}' has a plausible non-negative value ({val}).",
                            independence=EvidenceIndependence.INDEPENDENT,
                        )
                    )

    # 2. Pay period plausibility (for payslip)
    start_field = fields.get("pay_period_start")
    end_field = fields.get("pay_period_end")
    if start_field and end_field and start_field.normalized_value and end_field.normalized_value:
        cid = "PLAUSIBILITY_PAY_PERIOD_RANGE"
        try:
            d_start = datetime.strptime(str(start_field.normalized_value), "%Y-%m-%d")
            d_end = datetime.strptime(str(end_field.normalized_value), "%Y-%m-%d")
            duration_days = (d_end - d_start).days
            if duration_days < 0:
                checks.append(
                    VerificationCheck(
                        check_id=cid,
                        applies=True,
                        status="failed",
                        plain_explanation=f"Pay period end date ({d_end.date()}) is earlier than start date ({d_start.date()}).",
                        independence=EvidenceIndependence.INDEPENDENT,
                    )
                )
            elif duration_days > 62:
                checks.append(
                    VerificationCheck(
                        check_id=cid,
                        applies=True,
                        status="failed",
                        plain_explanation=f"Pay period duration ({duration_days} days) exceeds plausible single pay period length.",
                        independence=EvidenceIndependence.INDEPENDENT,
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        check_id=cid,
                        applies=True,
                        status="passed",
                        plain_explanation=f"Pay period duration ({duration_days} days) is plausible.",
                        independence=EvidenceIndependence.INDEPENDENT,
                    )
                )
        except Exception as e:
            checks.append(
                VerificationCheck(
                    check_id=cid,
                    applies=False,
                    applies_reason=f"Date parsing error: {e}",
                    status="indeterminate",
                    plain_explanation="Could not verify pay period dates.",
                )
            )

    # 3. Payment date vs period end
    pay_date_field = fields.get("payment_date")
    if pay_date_field and end_field and pay_date_field.normalized_value and end_field.normalized_value:
        cid = "PLAUSIBILITY_PAYMENT_TIMING"
        try:
            d_pay = datetime.strptime(str(pay_date_field.normalized_value), "%Y-%m-%d")
            d_end = datetime.strptime(str(end_field.normalized_value), "%Y-%m-%d")
            offset_days = (d_pay - d_end).days
            # Payment typically occurs between -5 days (end of month advance) and +35 days
            if -5 <= offset_days <= 35:
                checks.append(
                    VerificationCheck(
                        check_id=cid,
                        applies=True,
                        status="passed",
                        plain_explanation=f"Disbursement date ({d_pay.date()}) is chronologically plausible relative to pay period end ({d_end.date()}, offset: {offset_days} days).",
                        independence=EvidenceIndependence.INDEPENDENT,
                    )
                )
            else:
                checks.append(
                    VerificationCheck(
                        check_id=cid,
                        applies=True,
                        status="failed",
                        plain_explanation=f"Payment date ({d_pay.date()}) is unusually offset ({offset_days} days) from pay period end ({d_end.date()}).",
                        independence=EvidenceIndependence.INDEPENDENT,
                    )
                )
        except Exception:
            pass

    return checks
