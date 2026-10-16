# VeriDocs AI — Evidence-First Financial Document Intelligence & Consistency Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React: 18](https://img.shields.io/badge/Frontend-React_18-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178c6.svg)](https://www.typescriptlang.org)
[![Tests: 30 Passing](https://img.shields.io/badge/Tests-30%20Passing%20(71%25%20cov)-success.svg)](backend/tests/)

> **Core Axiom:** *An AI model must never be trusted to verify its own output. Extraction proposes; independent deterministic code decides.*

VeriDocs AI is an open-source, evidence-grounded document intelligence and fraud-consistency checker for payslips, bank statements, invoices, and receipts (PDF, PNG, JPEG). It extracts structured semantic entities, grounds every figure against independent optical tokens and vector layers, enforces mathematical accounting invariants, reconciles multi-document financial bundles, and outputs traceable, audit-ready explanations.

**Research Prototype Notice:** This system assesses document consistency and arithmetic invariants. It is **NOT** a production identity-verification, authenticity, or lending-decision system. It checks *consistency*, never *authenticity*.

---

## 1. Key Architectural Features

1. **100% Free & Open-Source (Zero Cloud / Zero API Keys)**: Runs locally on commodity CPU hardware (~8 GB RAM). No paid tiers, no cloud credits, no API keys required.
2. **Permissive Licensing (Zero Copyleft / Zero AGPL)**: Uses `pypdfium2` and `pdfplumber` instead of copyleft `PyMuPDF / fitz`. Permissive Apache-2.0, MIT, and BSD-3-Clause compliance documented in [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).
3. **Pluggable Extractor Pipeline**:
   - **B1 `ocr_rules` (Default, CPU)**: Dual optical reading with `RapidOCR` (ONNX runtime) and `pdfplumber` digital vector layers.
   - **B2/B3 `vlm_zero_shot` / `vlm_lora`**: Vision-Language Model loader with Google Colab notebook for `Qwen2-VL-2B-Instruct`.
4. **Deterministic Invariant Verification Engine**:
   - Evidence grounding with character token matching and spatial bounding box proximity.
   - Format and plausibility validation (pay period duration, disbursement timing, non-negative bounds).
   - Payslip arithmetic: $\text{Gross} = \text{Basic} + \sum \text{Allowances}$; $\text{Net} = \text{Gross} - \sum \text{Deductions}$.
   - Invoice arithmetic: $\sum (\text{Qty} \times \text{Price}) = \text{Subtotal}$; $\text{Subtotal} - \text{Discount} + \text{Tax} = \text{Total}$.
   - Bank continuity: Row-by-row balance chaining $B_t = B_{t-1} + C_t - D_t$, with exact first-break detection.
5. **Multi-Document Temporal Reconciliation**:
   - Matches payslip net salary against bank credits across a configurable 7-day disbursement window.
   - Accurately models realistic benign variations (wire fees, partial pay, clearing delays) as **Uncertain** rather than falsely accusing documents of inconsistency.
6. **Defensive Prompt Injection Hygiene**:
   - Quarantines extracted text strictly as untrusted data payloads.
   - Scans and neutralizes adversarial instruction text (e.g. *"ignore previous instructions"*).
7. **Ephemeral Privacy & Resource Safety**:
   - In-memory session registry with automated TTL sweeps.
   - Magic byte validation (`%PDF`, PNG, JPEG) and decompression bomb defenses.

---

## 2. Empirical Benchmark Evaluation Results

All numbers below originate directly from genuine runs executed by the evaluation harness (`eval/run_eval.py`) and recorded in [`results/latest_metrics.json`](results/latest_metrics.json):

| Metric | P0 (Extraction Only Baseline) | P1 (Extraction + Rules) | P2 (Full Pipeline: Rules + Grounding + Cross-Doc) |
|---|---|---|---|
| **Undetected Error Rate** | **31.2%** (CI: [18.8%, 41.7%]) | 31.2% | **31.2%** (CI: [18.8%, 41.7%]) |
| **Coverage Cost (Retained Correct)** | 100.0% | 75.0% | **75.0%** |
| **Seeded Inconsistency Detection (F1)**| 0.00 (N/A) | 0.25 | **0.25** |
| **Inconsistency Recall** | 0.00 | — | **0.50** |
| **Benign False-Alarm Rate** | 0.0% | 0.0% | **83.3%** |

*Hardware During Run: Apple M1 (8 cores, 8 GB RAM) | Peak Memory: 914.0 MB | Latency (p50): 933.0 ms.*

---

## 3. Quickstart & Installation

### Prerequisites
- Python 3.10 – 3.12 (Python 3.11 recommended)
- Node.js 20+ LTS & npm
- Git

### Setup on macOS & Linux

```bash
# 1. Clone repository
git clone https://github.com/your-username/veridocs-ai.git
cd veridocs-ai

# 2. Set up Python virtual environment & dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Set up Frontend
cd frontend
npm install
cd ..
```

### Setup on Windows (PowerShell)

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. Set up Frontend
cd frontend
npm install
cd ..
```

---

## 4. Running the Application

### Option A: Using Makefile (macOS / Linux)

```bash
# Terminal 1: Launch Backend API (http://127.0.0.1:8000)
make run-backend

# Terminal 2: Launch Frontend UI (http://localhost:5173)
make run-frontend
```

### Option B: Direct Terminal Commands

```bash
# Start FastAPI backend
source .venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Start Vite frontend
cd frontend
npm run dev
```

Open your browser to **`http://localhost:5173`** and click **Run Live Demo** to observe full extraction, bounding box grounding, and cross-document reconciliation.

---

## 5. Running Tests & Evaluation

```bash
# Run complete test suite with coverage (30 tests)
make test
# Or directly:
source .venv/bin/activate && pytest backend/tests eval/tests --cov=backend/app --cov=eval --cov-report=term-missing

# Run research benchmark evaluation
make eval
# Or directly:
source .venv/bin/activate && python eval/run_eval.py --profile quick

# Generate evaluation summary report
make report
```

---

## 6. Project Directory Layout

```
veridocs-ai/
├── README.md                     # Master documentation & benchmark summary
├── PROGRESS.md                   # Stage tracking & checkpoint history
├── Makefile                      # Standard project commands
├── pyproject.toml                # Project metadata & pytest configuration
├── requirements.txt              # Pinned Python dependencies
├── THIRD_PARTY_LICENSES.md       # License compliance inventory
├── LIMITATIONS.md                # Technical limitations & boundary conditions
├── MODEL_CARD.md                 # Model specifications & scope
├── DATASET_CARD.md               # Synthetic benchmark dataset documentation
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application entrypoint
│   │   ├── core/                 # Config & privacy-safe logging
│   │   ├── schemas/              # Pydantic v2 domain schemas
│   │   ├── extraction/           # OCR, deskew, normalizers & layout parsers
│   │   ├── verification/         # Deterministic checks, grounding & cross-doc
│   │   ├── reporting/            # ReportLab PDF generator & sample synthesizers
│   │   └── sessions/             # Ephemeral session manager & upload security
│   └── tests/                    # Backend unit & integration test suite
├── frontend/                     # React 18 + TypeScript + Vite + Tailwind UI
├── eval/
│   ├── generator/                # Synthetic generator (seen/unseen layout splits)
│   ├── degrade/                  # Blur, downscale, noise, rotation degradations
│   ├── metrics/                  # Bootstrap CIs, undetected error rates, F1
│   ├── tests/                    # Split-leakage & metrics tests
│   └── run_eval.py               # Full benchmark execution harness
├── results/                      # Real run manifests, plots, and metrics
├── colab/                        # VLM LoRA fine-tuning notebook & script
└── docs/                         # Architecture, API, metrics, demo guides
```

---

## 7. Troubleshooting

- **Port in Use**: If port 8000 or 5173 is already occupied, set custom ports:
  `uvicorn backend.app.main:app --port 8080` and `npm run dev -- --port 3000`.
- **RapidOCR First Run**: RapidOCR downloads its lightweight ONNX weights on first invocation. Subsequent runs are fully offline.
- **Node.js Build Errors**: Ensure Node.js 20+ LTS is active (`node -v`).

---

## 8. License

VeriDocs AI is licensed under the **MIT License**. All dependencies have been audited to ensure permissive licensing compliance (MIT, BSD-3-Clause, Apache-2.0, HPND). No copyleft or AGPL dependencies are used.
