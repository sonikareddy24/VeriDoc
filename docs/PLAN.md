# VeriDocs AI — Architecture & Implementation Plan

## 1. Project Purpose & Core Principle
VeriDocs AI is an evidence-first financial document intelligence and consistency verification system. It processes payslips, bank statements, invoices, and receipts (PDF, PNG, JPEG), extracts structured semantic fields, grounds every extracted value against independent deterministic evidence, conducts cross-document reconciliation, and yields fully traceable, audit-ready explanations.

**Core Axiom**: *An AI extraction model must never be trusted to verify its own output. Extraction proposes; independent deterministic code decides.*

---

## 2. Chosen Stack, Justifications & Licenses

| Component / Library | Version / Tool | Justification | License |
|---|---|---|---|
| **Runtime Language** | Python 3.11.15 | Stable, high performance on arm64 Apple Silicon | PSF License |
| **API Framework** | FastAPI (>=0.110.0) | High-speed async ASGI framework with OpenAPI generation | MIT |
| **Server** | Uvicorn (>=0.29.0) | Lightweight, standard ASGI production server | BSD-3-Clause |
| **Data Validation** | Pydantic v2 (>=2.6.0) | Fast Rust-backed schema validation and serialization | MIT |
| **PDF Rasterization** | pypdfium2 (>=4.30.0) | Render PDF pages to images cleanly; avoids AGPL | Apache-2.0 / BSD-3-Clause |
| **PDF Text Layer** | pdfplumber (>=0.11.0) | Layout-aware digital text extraction without copyleft | MIT |
| **Independent OCR** | rapidocr-onnxruntime (>=1.3.0) | Self-contained CPU OCR with word boxes and confidences | Apache-2.0 |
| **Image Processing** | Pillow (>=10.2.0) | Robust image loading, transformation, decompression defense | HPND |
| **Computer Vision** | opencv-python-headless (>=4.9.0) | Deskewing, rotation correction, blur estimation | Apache-2.0 |
| **Fuzzy Matching** | rapidfuzz (>=3.6.0) | Fast C++ Levenshtein/token ratio matching for text evidence | MIT |
| **Report Generation** | reportlab (>=4.1.0) | Programmatic PDF creation for audit summaries | BSD-3-Clause |
| **Data Generation** | Faker (>=24.0.0) | Synthetic entity and transaction generation | MIT |
| **Statistical Analysis** | numpy (>=1.26.0), scipy (>=1.12.0) | Bootstrap confidence intervals, numerical arrays | BSD-3-Clause |
| **Visualization** | matplotlib (>=3.8.0) | Evaluation curve and metric chart generation | Matplotlib / PSF |
| **Frontend Framework** | React 18 + Vite + TypeScript | Modern, high performance, strict typed single-page application | MIT |
| **Styling** | Tailwind CSS v3 | Utility-first styling for fintech design system | MIT |
| **Icons** | Lucide React | Clean, professional UI icons | ISC |
| **Testing** | pytest, pytest-cov, httpx | Async test client, unit and integration coverage | MIT / BSD-3-Clause |
| **Optional VLM** | Qwen2-VL-2B-Instruct | Lightweight open-weight Vision-Language Model for Colab | Apache-2.0 |

---

## 3. Risks & Mitigations

1. **Risk: OCR Hallucination or Mismatch on Complex Tables**
   - *Mitigation*: Dual-source evidence extraction (PDF text layer when present + RapidOCR on image render). Explicit token grounding requirement with strict exact matching for numbers.
2. **Risk: Copyleft / AGPL Contamination**
   - *Mitigation*: PyMuPDF (`fitz`) is strictly prohibited. Only `pypdfium2` and `pdfplumber` are used.
3. **Risk: Prompt Injection in Uploaded Documents**
   - *Mitigation*: Extracted text is always sanitized and treated strictly as data payloads inside JSON, never interpolated into executable prompts or shell commands. Prompt injection patterns are flagged as informational findings.
4. **Risk: Resource Exhaustion on 8 GB RAM Machine**
   - *Mitigation*: Stream processing of pages, strict limit of max 10 pages per document, session TTL cleanup, memory-safe image resizing and decompression protection.
5. **Risk: False Accusations of Fraud**
   - *Mitigation*: Clear taxonomy: "Supported", "Inconsistent", "Uncertain", "Unreadable". Never emit "fraud" or "tampered". Benign business variations (bank fees, timing offsets, partial pays) are explicitly modeled as "Uncertain" rather than "Inconsistent".

---

## 4. Stage Plan

- **Stage 1: Inspect & Plan** *(Completed)*: Environment verified, stack locked, licenses vetted.
- **Stage 2: Foundation**: Project scaffold, Pydantic schemas, config system, structured logging, health check, Makefile.
- **Stage 3: Extraction**: B1 `ocr_rules` engine (RapidOCR + pdfplumber), layout-aware parsers (Payslip, Bank Statement, Invoice), amount/date normalizers, quality gate.
- **Stage 4: Verification Engine**: Independent grounding, arithmetic validation, running balance continuity, cross-document reconciliation, injection hygiene.
- **Stage 5: API & Frontend**: FastAPI endpoints (sessions, documents, analysis, reports), React + TypeScript + Vite + Tailwind UI with interactive evidence viewer.
- **Stage 6: Research Evaluation & 6b Colab**: Synthetic data generator (seen vs unseen layouts, seeded inconsistencies, degradations), pipeline evaluation (P0 vs P1 vs P2), metrics, bootstrap CIs, plots, Colab LoRA notebook.
- **Stage 7: Test & Debug**: Comprehensive pytest suite (unit, integration, edge cases), frontend typecheck/build.
- **Stage 8: Documentation & Handover**: Complete guides, architecture diagrams, research report template, demo walkthrough, interview Q&A.
