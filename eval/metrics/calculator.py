"""Evaluation metrics calculator for financial document intelligence research.
Implements:
1. Exact match accuracy & normalized Levenshtein distance
2. Undetected Error Rate (headline metric): incorrect fields marked Supported / all incorrect fields
3. Coverage Cost: correct fields marked Supported / all correct fields
4. False-Alarm Rate: correct fields flagged Inconsistent / all correct fields
5. Seeded Inconsistency Detection: Precision, Recall, F1, FPR, FNR
6. Resampling bootstrap 95% confidence intervals
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from rapidfuzz.distance import Levenshtein


def compute_field_metrics(
    extracted_fields: Dict[str, Any],
    ground_truth_fields: Dict[str, Any],
    field_statuses: Dict[str, str],
) -> Dict[str, Any]:
    """Calculates field-level extraction and verification accuracy metrics."""
    total_gt_fields = len(ground_truth_fields)
    exact_matches = 0
    numeric_errors = 0
    numeric_total = 0
    edit_distances = []

    # Pipeline status counts
    incorrect_marked_supported = 0
    all_incorrect_fields = 0
    correct_marked_supported = 0
    correct_marked_inconsistent = 0
    all_correct_fields = 0

    for fname, gt_val in ground_truth_fields.items():
        ext_val = extracted_fields.get(fname)
        status = field_statuses.get(fname, "Uncertain")

        is_correct = False
        if ext_val is not None:
            if isinstance(gt_val, (int, float)) and isinstance(ext_val, (int, float)):
                numeric_total += 1
                if abs(float(gt_val) - float(ext_val)) < 0.05:
                    is_correct = True
                    exact_matches += 1
                else:
                    numeric_errors += 1
            else:
                s_gt = str(gt_val).strip().lower()
                s_ext = str(ext_val).strip().lower()
                dist = Levenshtein.normalized_distance(s_gt, s_ext)
                edit_distances.append(dist)
                if s_gt == s_ext or dist < 0.15:
                    is_correct = True
                    exact_matches += 1
        else:
            if isinstance(gt_val, (int, float)):
                numeric_total += 1
                numeric_errors += 1

        if is_correct:
            all_correct_fields += 1
            if status == "Supported":
                correct_marked_supported += 1
            elif status == "Inconsistent":
                correct_marked_inconsistent += 1
        else:
            all_incorrect_fields += 1
            if status == "Supported":
                incorrect_marked_supported += 1

    acc = exact_matches / max(1, total_gt_fields)
    num_err_rate = numeric_errors / max(1, numeric_total)
    mean_edit_dist = float(np.mean(edit_distances)) if edit_distances else 0.0

    # Headline verification metrics
    undetected_rate = (
        incorrect_marked_supported / all_incorrect_fields
        if all_incorrect_fields > 0
        else 0.0
    )
    coverage_cost = (
        correct_marked_supported / all_correct_fields
        if all_correct_fields > 0
        else 1.0
    )
    false_alarm_rate = (
        correct_marked_inconsistent / all_correct_fields
        if all_correct_fields > 0
        else 0.0
    )

    return {
        "accuracy": acc,
        "numeric_error_rate": num_err_rate,
        "mean_edit_distance": mean_edit_dist,
        "undetected_error_rate": undetected_rate,
        "coverage_cost": coverage_cost,
        "false_alarm_rate": false_alarm_rate,
        "all_incorrect": all_incorrect_fields,
        "undetected_errors": incorrect_marked_supported,
        "all_correct": all_correct_fields,
        "correct_supported": correct_marked_supported,
    }


def compute_inconsistency_detection_metrics(
    y_true: List[bool], y_pred: List[bool]
) -> Dict[str, float]:
    """Computes document-level Precision, Recall, F1, FPR, FNR for seeded inconsistency detection."""
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt and yp)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and yp)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt and not yp)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and not yp)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "fnr": fnr,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def compute_bootstrap_ci(
    data: List[float], n_bootstrap: int = 1000, alpha: float = 0.05
) -> Tuple[float, float, float]:
    """Computes resampled bootstrap 95% confidence intervals (mean, lower, upper)."""
    if not data:
        return 0.0, 0.0, 0.0
    arr = np.array(data)
    boot_means = []
    n = len(arr)
    for _ in range(n_bootstrap):
        sample = np.random.choice(arr, size=n, replace=True)
        boot_means.append(float(np.mean(sample)))

    mean_val = float(np.mean(arr))
    lower = float(np.percentile(boot_means, (alpha / 2) * 100))
    upper = float(np.percentile(boot_means, (1 - alpha / 2) * 100))
    return round(mean_val, 4), round(lower, 4), round(upper, 4)
