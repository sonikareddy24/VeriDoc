"""Unit tests for research evaluation metrics."""

from eval.metrics.calculator import (
    compute_field_metrics,
    compute_inconsistency_detection_metrics,
    compute_bootstrap_ci,
)


def test_field_metrics_calculation():
    gt = {
        "net_salary": 75000.0,
        "employer_name": "Infosys Ltd",
        "employee_id": "EMP-1001",
    }

    # Case 1: Baseline P0 marks all extracted fields as Supported
    # Extracted net_salary is WRONG (tampered), but P0 marks it Supported -> undetected error!
    extracted = {
        "net_salary": 80000.0,  # Wrong!
        "employer_name": "Infosys Ltd",  # Correct
        "employee_id": "EMP-1001",  # Correct
    }
    statuses_p0 = {
        "net_salary": "Supported",
        "employer_name": "Supported",
        "employee_id": "Supported",
    }
    m_p0 = compute_field_metrics(extracted, gt, statuses_p0)
    assert m_p0["undetected_error_rate"] == 1.0  # 1 out of 1 incorrect field falsely accepted
    assert m_p0["coverage_cost"] == 1.0

    # Case 2: P2 catches the arithmetic mismatch on net_salary -> marks it Inconsistent
    statuses_p2 = {
        "net_salary": "Inconsistent",
        "employer_name": "Supported",
        "employee_id": "Supported",
    }
    m_p2 = compute_field_metrics(extracted, gt, statuses_p2)
    assert m_p2["undetected_error_rate"] == 0.0  # Zero incorrect fields marked Supported!
    assert m_p2["coverage_cost"] == 1.0  # All correct fields still marked Supported


def test_inconsistency_detection_metrics():
    y_true = [True, False, True, False]
    y_pred = [True, False, False, False]  # 1 TP, 1 FN, 2 TN, 0 FP

    metrics = compute_inconsistency_detection_metrics(y_true, y_pred)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.5
    assert round(metrics["f1"], 2) == 0.67
    assert metrics["fpr"] == 0.0


def test_bootstrap_ci():
    data = [0.85, 0.86, 0.84, 0.88, 0.85, 0.87, 0.83, 0.86]
    mean, lower, upper = compute_bootstrap_ci(data, n_bootstrap=500)
    assert 0.80 <= lower <= mean <= upper <= 0.90
