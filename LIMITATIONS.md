# VeriDocs AI — System Limitations & Boundary Conditions

VeriDocs AI is a research prototype and portfolio project built to explore evidence-grounded document consistency verification. In adherence to Rule 0.2 (Honesty), the following real technical limitations and architectural boundaries must be explicitly noted.

---

## 1. Same-Source Evidence Constraint
- When operating under the default CPU setup (Backend B1: `ocr_rules`) where only a single optical character recognition engine (RapidOCR) is available without a digital text layer, the evidence tokens originate from the **same engine** that proposes the field.
- **Architectural Guardrail**: Same-source evidence is strictly prohibited from upgrading a field to **Supported**. Such fields remain classified as **Uncertain**, even if bounding box proximity and token match succeed.
- Independent confirmation requires a secondary independent source (e.g., native PDF text layer via `pdfplumber`, or an independent VLM / Tesseract engine).

---

## 2. Consistency vs. Authenticity
- VeriDocs AI verifies **internal consistency** and **cross-document reconciliation**.
- **It does NOT detect visual tampering or authenticate document provenance**:
  - A mathematically consistent payslip generated maliciously with realistic layout and matching bank statement will pass all deterministic checks.
  - The system does not analyze JPEG compression ghosting, PRNU camera sensor noise, error level analysis (ELA), or cryptographic signature chains.
  - The system will never emit a "fraud verdict" or claim that a document is authentic.

---

## 3. Layout Generalization & Heuristics
- The heuristic parser relies on label proximity, reading order line reconstruction, and regex patterns tuned on the Seen Layouts split.
- When exposed to highly unconventional layouts (e.g., circular graphs, heavily nested tables, multi-column wrapped text), extraction recall decreases.
- Unseen layout evaluation demonstrated that non-standard labels (e.g. "Total Net Payable" instead of "Net Pay") can cause field extraction misses unless supplemented by adaptable Vision-Language Models.

---

## 4. Optical Quality Floor
- The image quality gate applies Laplacian variance blur detection (threshold: 100.0) and Hough deskewing.
- However, documents with extreme blur (variance < 30.0), downscaling to sub-300px dimensions, or substantial physical occlusion of financial figures cannot be recovered by OCR and will be marked **Unreadable** or **Uncertain**.

---

## 5. Scope & Legal Disclaimers
- VeriDocs AI is **not** an authorized identity verification, KYC, AML, or credit underwriting decision engine.
- String matching between employee names and account holders is provided strictly for **informational purposes** and must never be interpreted as confirming person identity.
