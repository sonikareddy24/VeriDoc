# Dataset Card: VeriDocs AI Synthetic Financial Benchmark

## 1. Dataset Summary
The VeriDocs AI Synthetic Financial Benchmark is a 100% synthetically generated, fully reproducible dataset designed to evaluate document extraction, independent evidence grounding, and deterministic consistency verification under seen and unseen layout conditions.

No real-world personal identifiable information (PII) or sensitive banking records are present in this dataset.

---

## 2. Dataset Generation Methodology
- **Generation Engine**: Python `Faker` (locale: `en_IN`) with pinned seed (`seed=42`).
- **Rendering Engine**: ReportLab Open Source (BSD-3-Clause) drawing directly to PDF bitmaps and vector layers.
- **Image Degradations**: Applied post-split using OpenCV headless:
  - Gaussian blur (Laplacian variance degradation)
  - Downscaling / resolution loss (to 25-40% original dimensions)
  - Small-angle rotation (3° - 12°) and 90° orientation inversion
  - JPEG compression artifacts (quality 10 - 50)
  - Gaussian additive noise ($\sigma = 15 - 65$)
  - Partial rectangular field occlusion

---

## 3. Split Policy & Leakage Prevention
To guarantee rigorous generalization assessment:
- **Seen Layouts (Dev / Training Split)**: Layouts 1 and 2 (Corporate Tabular and Modern 2-Column).
- **Unseen Layouts (Final Evaluation Split)**: Layouts 3 and 4 (Minimal Compact Grid and Bordered Form with alternative terminology e.g. "Take-home", "Total Net Payable").
- **Zero-Leakage Enforcement**: Evaluated in `eval/tests/test_split_leakage.py`. No synthetic person name, company name, or document ID appears in both splits ($\text{Seen} \cap \text{Unseen} = \emptyset$).

---

## 4. Inconsistency Types & Benign Negatives

### 4.1 Seeded Simulated Inconsistencies (Positive Ground Truth $y=1$)
- `net_pay_arithmetic_mismatch`: Net pay deliberately manipulated by $\pm$ 5,000 INR relative to gross - deductions.
- `bank_running_balance_break`: Transaction row balance broken by $\pm$ 5,000 INR.
- `invoice_total_mismatch`: Subtotal - discount + tax $\ne$ grand total.
- `deposit_amount_mismatch`: Payslip net salary $\ne$ bank salary credit.

### 4.2 Realistic Benign Variations (Negative Ground Truth $y=0$)
To ensure the system does not produce high false alarms on legitimate business variations, the following are included:
- **Bank Wire Fee**: Bank credit is net salary minus 100 INR.
- **Disbursement Timing Delay**: Bank credit cleared 1–4 days after payslip payment date.
- **Partial Pay**: 50% salary advance disbursement.
*Requirement*: Must produce status **Uncertain**, NOT **Inconsistent**.
