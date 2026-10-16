"""Deterministic bank statement continuity, running-balance chaining, and chronological verification."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from backend.app.schemas.common import (
    EvidenceIndependence,
    ExtractedField,
    VerificationCheck,
)


def verify_bank_statement_continuity(
    fields: Dict[str, ExtractedField],
    structured_data: Optional[Dict[str, Any]] = None,
    tolerance: float = 0.05,
) -> List[VerificationCheck]:
    checks: List[VerificationCheck] = []

    open_val = fields.get("opening_balance", ExtractedField(name="open")).normalized_value
    close_val = fields.get("closing_balance", ExtractedField(name="close")).normalized_value

    transactions = []
    if structured_data:
        transactions = structured_data.get("transactions") or []

    # 1. Row-by-row Running Balance Chain Check
    if transactions and len(transactions) >= 2:
        break_found = False
        for idx in range(1, len(transactions)):
            prev_row = transactions[idx - 1]
            curr_row = transactions[idx]

            prev_bal = prev_row.get("running_balance")
            curr_bal = curr_row.get("running_balance")
            debit = curr_row.get("debit") or 0.0
            credit = curr_row.get("credit") or 0.0

            if prev_bal is not None and curr_bal is not None:
                expected_curr_bal = prev_bal + credit - debit
                diff = abs(curr_bal - expected_curr_bal)
                if diff > tolerance:
                    break_found = True
                    checks.append(
                        VerificationCheck(
                            check_id="BANK_RUNNING_BALANCE_CHAIN",
                            applies=True,
                            status="failed",
                            evidence_refs=[
                                f"Row {prev_row.get('row_idx', idx)}: Balance {prev_bal:.2f}",
                                f"Row {curr_row.get('row_idx', idx+1)}: Debit {debit:.2f}, Credit {credit:.2f}, Actual Balance {curr_bal:.2f}",
                            ],
                            plain_explanation=(
                                f"Running-balance continuity break detected at row {curr_row.get('row_idx', idx+1)}! "
                                f"Previous balance ({prev_bal:.2f}) + credit ({credit:.2f}) - debit ({debit:.2f}) "
                                f"yields expected balance {expected_curr_bal:.2f}, but statement shows {curr_bal:.2f} "
                                f"(break of {diff:.2f})."
                            ),
                            independence=EvidenceIndependence.INDEPENDENT,
                        )
                    )
                    break  # Report the first break as per specification

        if not break_found:
            checks.append(
                VerificationCheck(
                    check_id="BANK_RUNNING_BALANCE_CHAIN",
                    applies=True,
                    status="passed",
                    plain_explanation=(
                        f"Running balance continuity holds seamlessly across all {len(transactions)} transaction rows."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
    else:
        checks.append(
            VerificationCheck(
                check_id="BANK_RUNNING_BALANCE_CHAIN",
                applies=False,
                applies_reason="Fewer than 2 sequential transaction rows available.",
                status="indeterminate",
                plain_explanation="Skipped running-balance check due to insufficient transaction rows.",
            )
        )

    # 2. Overall Opening + Total Credits - Total Debits == Closing Balance
    if open_val is not None and close_val is not None and transactions:
        tot_credits = sum(float(tx.get("credit") or 0.0) for tx in transactions)
        tot_debits = sum(float(tx.get("debit") or 0.0) for tx in transactions)
        expected_close = open_val + tot_credits - tot_debits
        diff = abs(close_val - expected_close)

        if diff <= tolerance:
            checks.append(
                VerificationCheck(
                    check_id="BANK_OPENING_CLOSING_CONTINUITY",
                    applies=True,
                    status="passed",
                    plain_explanation=(
                        f"Opening balance ({open_val:.2f}) + total credits ({tot_credits:.2f}) - "
                        f"total debits ({tot_debits:.2f}) matches closing balance ({close_val:.2f}) within tolerance ({diff:.2f} <= {tolerance})."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    check_id="BANK_OPENING_CLOSING_CONTINUITY",
                    applies=True,
                    status="failed",
                    plain_explanation=(
                        f"Statement balance mismatch: Opening ({open_val:.2f}) + credits ({tot_credits:.2f}) - "
                        f"debits ({tot_debits:.2f}) expects closing balance {expected_close:.2f}, "
                        f"but stated closing balance is {close_val:.2f} (discrepancy: {diff:.2f})."
                    ),
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )
    else:
        checks.append(
            VerificationCheck(
                check_id="BANK_OPENING_CLOSING_CONTINUITY",
                applies=False,
                applies_reason="Missing opening balance, closing balance, or transaction set.",
                status="indeterminate",
                plain_explanation="Skipped opening/closing continuity check due to missing fields.",
            )
        )

    # 3. Transaction Date Chronology
    if transactions and len(transactions) >= 2:
        chronology_valid = True
        for idx in range(1, len(transactions)):
            d_prev_str = transactions[idx - 1].get("date")
            d_curr_str = transactions[idx].get("date")
            if d_prev_str and d_curr_str:
                try:
                    d_prev = datetime.strptime(d_prev_str, "%Y-%m-%d")
                    d_curr = datetime.strptime(d_curr_str, "%Y-%m-%d")
                    if d_curr < d_prev:
                        chronology_valid = False
                        checks.append(
                            VerificationCheck(
                                check_id="BANK_DATE_CHRONOLOGY",
                                applies=True,
                                status="failed",
                                plain_explanation=(
                                    f"Date chronological inversion detected at row {transactions[idx].get('row_idx', idx+1)}: "
                                    f"date {d_curr_str} appears after {d_prev_str}."
                                ),
                                independence=EvidenceIndependence.INDEPENDENT,
                            )
                        )
                        break
                except Exception:
                    pass
        if chronology_valid:
            checks.append(
                VerificationCheck(
                    check_id="BANK_DATE_CHRONOLOGY",
                    applies=True,
                    status="passed",
                    plain_explanation="All transaction dates follow chronological ordering.",
                    independence=EvidenceIndependence.INDEPENDENT,
                )
            )

    return checks
