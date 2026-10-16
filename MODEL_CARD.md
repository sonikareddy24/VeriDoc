# Model Card: VeriDocs AI Extraction & Verification Components

## 1. Model Details
- **System**: VeriDocs AI
- **Primary Engine**: RapidOCR (PP-OCRv4 ONNX runtime CPU pipeline)
  - Detection Model: `ch_PP-OCRv4_det_infer.onnx`
  - Recognition Model: `ch_PP-OCRv4_rec_infer.onnx`
  - Direction Classifier: `ch_ppocr_mobile_v2.0_cls_infer.onnx`
- **License**: Apache-2.0
- **Optional VLM Backend**: Qwen2-VL-2B-Instruct (Apache-2.0) via Hugging Face transformers.

---

## 2. Intended Use & Scope
- **Intended Use**: Academic research, portfolio demonstrations, layout parsing experimentation, and deterministic consistency checks across financial documents (payslips, bank statements, invoices).
- **Out-of-Scope / Prohibited Uses**:
  - Production identity verification (KYC/AML).
  - Automated credit lending or underwriting decisions.
  - Legal forensics or forensic fraud verdicts.
  - Real-world document authenticity certification.

---

## 3. Core Principle: Non-Self-Verifying AI
An AI extraction model (OCR or Vision-Language Model) must never be trusted to verify its own output. In VeriDocs AI:
- Extraction engines **propose** candidate field values.
- Independent, deterministic verification code **decides** whether a value is grounded, plausible, and mathematically consistent.
- Same-source evidence (where evidence originates from the same engine that performed extraction) is flagged as **Uncertain** and barred from self-promotion to **Supported**.

---

## 4. Factors, Risks & Biases
- **Language**: English and numerical financial formats. Non-Latin scripts are not supported in the default rule set.
- **Image Quality**: Significant motion blur, severe downscaling (< 400px), or heavy occlusions degrade OCR character recognition.
- **Unseen Layouts**: Layout generalizability is subject to heuristic parsing limitations when document formats deviate significantly from standard tabular structures.
