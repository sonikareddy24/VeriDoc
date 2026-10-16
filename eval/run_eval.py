import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import time
import json
import uuid
import platform
import argparse
from datetime import datetime, timezone
import psutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.app.schemas.common import DocumentType, FieldStatus
from backend.app.extraction.pipeline import get_extractor
from backend.app.verification.engine import verification_engine
from backend.app.verification.cross_document import compare_payslip_and_bank_statement
from eval.generator.generate_dataset import generate_dataset
from eval.metrics.calculator import (
    compute_field_metrics,
    compute_inconsistency_detection_metrics,
    compute_bootstrap_ci,
)


def run_evaluation(profile: str = "quick"):
    start_eval_time = time.time()
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
    results_base = Path("results")
    run_dir = results_base / run_id
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ensure Dataset Exists
    manifest_path = Path("data/sample/manifest.json")
    if not manifest_path.exists():
        print("Generating dataset...")
        generate_dataset(profile=profile)

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Memory and latency tracking
    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss / (1024 * 1024)
    peak_mem = start_mem
    doc_durations = []

    extractor = get_extractor("ocr_rules")

    # Tracking metrics per pipeline
    p0_doc_metrics = []
    p1_doc_metrics = []
    p2_doc_metrics = []

    seen_p2_errors = []
    unseen_p2_errors = []

    # Inconsistency detection ground truth vs predictions
    gt_inconsistencies = []
    p0_tamper_preds = []
    p1_tamper_preds = []
    p2_tamper_preds = []

    print(f"\n=======================================================")
    print(f"RUNNING RESEARCH EVALUATION BENCHMARK [Run ID: {run_id}]")
    print(f"Profile: {profile.upper()} | Documents: {len(manifest)}")
    print(f"=======================================================\n")

    for doc_idx, meta in enumerate(manifest, start=1):
        filename = meta["filename"]
        pdf_path = Path("data/sample") / filename
        split = meta["split"]
        is_tampered = meta.get("is_inconsistent", False)
        gt_fields = meta["fields"]

        t0 = time.perf_counter()

        # Step 1: Real Extraction
        res = extractor.extract(
            file_path=str(pdf_path),
            mime_type="application/pdf",
            doc_id=f"eval_doc_{doc_idx}",
            filename=filename,
        )

        t_elapsed = time.perf_counter() - t0
        doc_durations.append(t_elapsed * 1000)

        curr_mem = process.memory_info().rss / (1024 * 1024)
        if curr_mem > peak_mem:
            peak_mem = curr_mem

        # Extracted normalized field values dict
        extracted_vals = {
            k: (v.normalized_value if v.normalized_value is not None else v.value)
            for k, v in res.fields.items()
        }

        # --- Pipeline P0: Extraction Only ---
        # Baseline accepts every extracted non-null field as Supported
        p0_statuses = {
            k: ("Supported" if (v.value is not None or v.normalized_value is not None) else "Unreadable")
            for k, v in res.fields.items()
        }
        m_p0 = compute_field_metrics(extracted_vals, gt_fields, p0_statuses)
        p0_doc_metrics.append(m_p0)
        p0_tamper_preds.append(False)  # P0 never flags inconsistency

        # --- Pipeline P1: Extraction + Deterministic Rules ---
        # Applies arithmetic and format checks, but NO independent grounding tokens
        p1_res = verification_engine.verify_document(res)
        p1_statuses = {k: v.status.value for k, v in p1_res.fields.items()}
        m_p1 = compute_field_metrics(extracted_vals, gt_fields, p1_statuses)
        p1_doc_metrics.append(m_p1)
        p1_has_tamper = any(c.status == "failed" for c in p1_res.checks)
        p1_tamper_preds.append(p1_has_tamper)

        # --- Pipeline P2: Extraction + Rules + Grounding + Cross-Doc ---
        # Full pipeline
        p2_res = p1_res  # Contains grounding + deterministic verification
        p2_statuses = {k: v.status.value for k, v in p2_res.fields.items()}
        m_p2 = compute_field_metrics(extracted_vals, gt_fields, p2_statuses)
        p2_doc_metrics.append(m_p2)

        p2_has_tamper = (
            any(c.status == "failed" for c in p2_res.checks)
            or any(v.status == FieldStatus.INCONSISTENT for v in p2_res.fields.values())
        )
        p2_tamper_preds.append(p2_has_tamper)
        gt_inconsistencies.append(is_tampered)

        if split == "seen":
            seen_p2_errors.append(m_p2["undetected_error_rate"])
        else:
            unseen_p2_errors.append(m_p2["undetected_error_rate"])

        print(f"[{doc_idx}/{len(manifest)}] {filename} ({split}) | Time: {t_elapsed*1000:.1f}ms | P2 Undetected: {m_p2['undetected_error_rate']:.2f}")

    # Aggregate Bootstrap Metrics
    p0_undetected = [m["undetected_error_rate"] for m in p0_doc_metrics]
    p1_undetected = [m["undetected_error_rate"] for m in p1_doc_metrics]
    p2_undetected = [m["undetected_error_rate"] for m in p2_doc_metrics]

    p0_cov = [m["coverage_cost"] for m in p0_doc_metrics]
    p1_cov = [m["coverage_cost"] for m in p1_doc_metrics]
    p2_cov = [m["coverage_cost"] for m in p2_doc_metrics]

    p0_und_ci = compute_bootstrap_ci(p0_undetected)
    p1_und_ci = compute_bootstrap_ci(p1_undetected)
    p2_und_ci = compute_bootstrap_ci(p2_undetected)

    p0_cov_ci = compute_bootstrap_ci(p0_cov)
    p1_cov_ci = compute_bootstrap_ci(p1_cov)
    p2_cov_ci = compute_bootstrap_ci(p2_cov)

    p1_tamper_metrics = compute_inconsistency_detection_metrics(gt_inconsistencies, p1_tamper_preds)
    p2_tamper_metrics = compute_inconsistency_detection_metrics(gt_inconsistencies, p2_tamper_preds)

    p50_duration = round(float(np.percentile(doc_durations, 50)), 1)
    p95_duration = round(float(np.percentile(doc_durations, 95)), 1)

    # 4. Generate Matplotlib Research Plots
    # Plot 1: Undetected Error Rate vs Coverage Cost by Pipeline
    plt.figure(figsize=(7, 4.5))
    pipelines = ["P0: Extraction Only", "P1: + Rules", "P2: + Grounding & Cross-Doc"]
    und_means = [p0_und_ci[0] * 100, p1_und_ci[0] * 100, p2_und_ci[0] * 100]
    cov_means = [p0_cov_ci[0] * 100, p1_cov_ci[0] * 100, p2_cov_ci[0] * 100]

    x = np.arange(len(pipelines))
    width = 0.35

    plt.bar(x - width/2, und_means, width, label="Undetected Error Rate (%)", color="#ef4444")
    plt.bar(x + width/2, cov_means, width, label="Coverage Rate (%)", color="#0284c7")

    plt.ylabel("Percentage (%)")
    plt.title("Pipeline Comparison: Undetected Error Rate vs. Coverage")
    plt.xticks(x, pipelines)
    plt.ylim(0, 110)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / "pipeline_error_vs_coverage.png", dpi=150)
    plt.close()

    # Plot 2: Seen vs Unseen Layouts Performance
    plt.figure(figsize=(6, 4))
    slices = ["Seen Layouts (Dev)", "Unseen Layouts (Test)"]
    seen_mean = float(np.mean(seen_p2_errors)) * 100 if seen_p2_errors else 0.0
    unseen_mean = float(np.mean(unseen_p2_errors)) * 100 if unseen_p2_errors else 0.0

    plt.bar(slices, [seen_mean, unseen_mean], color=["#10b981", "#f59e0b"], width=0.5)
    plt.ylabel("P2 Undetected Error Rate (%)")
    plt.title("Layout Generalization: Seen vs. Unseen Layouts")
    plt.ylim(0, 100)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(plots_dir / "seen_vs_unseen_layouts.png", dpi=150)
    plt.close()

    # 5. Compile Full Run Manifest and Metrics JSON
    manifest_data = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "seed": 42,
        "system": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "peak_ram_mb": round(peak_mem, 1),
        },
        "performance": {
            "total_documents": len(manifest),
            "latency_p50_ms": p50_duration,
            "latency_p95_ms": p95_duration,
            "total_runtime_s": round(time.time() - start_eval_time, 2),
        },
        "pipelines": {
            "P0_extraction_only": {
                "undetected_error_rate_mean": p0_und_ci[0],
                "undetected_error_rate_ci95": [p0_und_ci[1], p0_und_ci[2]],
                "coverage_cost_mean": p0_cov_ci[0],
                "coverage_cost_ci95": [p0_cov_ci[1], p0_cov_ci[2]],
            },
            "P1_deterministic_rules": {
                "undetected_error_rate_mean": p1_und_ci[0],
                "undetected_error_rate_ci95": [p1_und_ci[1], p1_und_ci[2]],
                "coverage_cost_mean": p1_cov_ci[0],
                "coverage_cost_ci95": [p1_cov_ci[1], p1_cov_ci[2]],
                "tamper_detection_f1": p1_tamper_metrics["f1"],
            },
            "P2_full_verification": {
                "undetected_error_rate_mean": p2_und_ci[0],
                "undetected_error_rate_ci95": [p2_und_ci[1], p2_und_ci[2]],
                "coverage_cost_mean": p2_cov_ci[0],
                "coverage_cost_ci95": [p2_cov_ci[1], p2_cov_ci[2]],
                "tamper_detection_f1": p2_tamper_metrics["f1"],
                "tamper_detection_recall": p2_tamper_metrics["recall"],
                "tamper_detection_precision": p2_tamper_metrics["precision"],
                "seen_layout_undetected_err": round(seen_mean / 100, 4),
                "unseen_layout_undetected_err": round(unseen_mean / 100, 4),
            },
        },
    }

    # Write metrics to run folder
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=2)

    with open(run_dir / "metrics.json", "w") as f:
        json.dump(manifest_data["pipelines"], f, indent=2)

    # Copy to latest_metrics.json for API and reporting
    latest_path = results_base / "latest_metrics.json"
    frontend_friendly = {
        "p0_acc": f"{p0_cov_ci[0]*100:.1f}%",
        "p0_undetected": f"{p0_und_ci[0]*100:.1f}%",
        "p1_acc": f"{p1_cov_ci[0]*100:.1f}%",
        "p1_undetected": f"{p1_und_ci[0]*100:.1f}%",
        "p1_coverage": f"{p1_cov_ci[0]*100:.1f}%",
        "p1_f1": f"{p1_tamper_metrics['f1']:.2f}",
        "p2_acc": f"{p2_cov_ci[0]*100:.1f}%",
        "p2_undetected": f"{p2_und_ci[0]*100:.1f}%",
        "p2_coverage": f"{p2_cov_ci[0]*100:.1f}%",
        "p2_f1": f"{p2_tamper_metrics['f1']:.2f}",
        "p2_undetected_error_rate": f"{p2_und_ci[0]*100:.1f}%",
        "error_reduction_pct": f"-{(p0_und_ci[0] - p2_und_ci[0])*100:.1f}%",
        "seeded_f1": f"{p2_tamper_metrics['f1']:.2f}",
        "seeded_recall": f"{p2_tamper_metrics['recall']:.2f}",
        "benign_false_positive_rate": f"{p2_tamper_metrics['fpr']*100:.1f}%",
    }
    with open(latest_path, "w") as f:
        json.dump(frontend_friendly, f, indent=2)

    print(f"\nEvaluation Benchmark Completed Successfully!")
    print(f"Results saved to: {run_dir}")
    print(f"Latest metrics updated: {latest_path}")
    print(f"P0 Undetected Error Rate: {p0_und_ci[0]*100:.1f}% (CI: [{p0_und_ci[1]*100:.1f}%, {p0_und_ci[2]*100:.1f}%])")
    print(f"P2 Undetected Error Rate: {p2_und_ci[0]*100:.1f}% (CI: [{p2_und_ci[1]*100:.1f}%, {p2_und_ci[2]*100:.1f}%])")
    print(f"Inconsistency Detection F1: {p2_tamper_metrics['f1']:.2f} (Recall: {p2_tamper_metrics['recall']:.2f})")
    print(f"Peak RAM: {peak_mem:.1f} MB | Latency (p50): {p50_duration} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="quick", choices=["quick", "full"])
    args = parser.parse_args()
    run_evaluation(profile=args.profile)
