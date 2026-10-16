# VeriDocs AI — 4-Minute Interview Demo Script & Technical Q&A

This document provides a structured, concise 4-minute demonstration script for technical presentations, along with 10 technical interview questions and answers based on the real implementation and empirical benchmark results.

*(Note: This project is an academic research and engineering prototype; no claim is made that it guarantees employment).*

---

## 4-Minute Demo Script

### Minute 0:00 – 0:45: The Problem & The Core Axiom
**Speaker Action**: Open browser to `http://localhost:5173`. Point to the header and the research disclaimer banner.
> "Today I'm presenting VeriDocs AI, an evidence-first financial document intelligence and consistency checker. In automated financial workflows, the standard practice is to trust a neural network or OCR model's probability score. But an AI model should never be trusted to verify its own output. Extraction proposes; independent code decides. VeriDocs AI is built around deterministic invariants, independent evidence grounding, and traceable auditing."

### Minute 0:45 – 1:45: Live Multi-Document Execution
**Speaker Action**: Click the **Run Live Demo** button in the navbar.
> "Let's run our live demonstration bundle. Notice that nothing is mocked: the backend generates synthetic PDFs, streams them through our dual reader—extracting both digital vector text with `pdfplumber` and rasterized optical text with `RapidOCR` on CPU—and reconstructs the layout. In under two seconds, we have full extraction and verification for both a payslip and a bank statement."

### Minute 1:45 – 2:45: Grounding & Bounding Box Inspection
**Speaker Action**: In the Extracted Semantic Fields table, click on `net_salary`. Show the Evidence Grounding Inspector on the right.
> "Notice the status chips: Supported, Inconsistent, Uncertain, and Unreadable. When I select `net_salary`, our Evidence Inspector displays the exact spatial bounding box on the page, the raw versus normalized value, and the matched independent tokens. Crucially, if evidence comes only from the same OCR engine that proposed it, our system deliberately flags it as Uncertain—because same-source evidence cannot self-certify."

### Minute 2:45 – 3:30: Deterministic Invariants & Benign Variations
**Speaker Action**: Scroll down to the Deterministic Verification Rules and Cross-Document Reconciliation cards.
> "Down here, we see our deterministic invariants at work: payslip gross arithmetic, net salary minus deductions, and bank running balance chaining row by row. Notice our cross-document reconciler: it matches the payslip net salary to the bank credit across a temporal window. When a benign variation occurs—like a 100-rupee wire fee or a 2-day bank clearing delay—our engine classifies it as Uncertain with an explanation, rather than throwing a false alarm."

### Minute 3:30 – 4:00: Auditing & Research Benchmarks
**Speaker Action**: Click **Audit PDF** to download the report, then switch to the **Research Benchmarks** tab.
> "Finally, we can download a fully traceable PDF audit report generated via ReportLab. Over in our Research Benchmarks tab, we display empirical results from our zero-leakage evaluation harness comparing extraction-only baselines against our full evidence-grounded pipeline. The entire system is 100% free, permissive-license compliant, and runs locally on CPU."

---

## 10-Question Technical Interview Q&A

### Q1: Why not just use an end-to-end multi-modal LLM like GPT-4o or Gemini to extract and verify the document in a single prompt?
**Answer**: Single-prompt verification violates the core principle of independent evidence. An LLM prompted to 'extract and verify' will readily hallucinate reasons why an incorrect figure is mathematically consistent to satisfy the prompt. Furthermore, in production fintech, passing sensitive PII to external paid cloud APIs introduces data residency, compliance, and recurring API cost risks. Our architecture keeps extraction lightweight, runs locally on CPU, and delegates all verification to deterministic code with zero hallucination risk.

### Q2: What is the "Same-Source Evidence" limitation, and how do you handle it?
**Answer**: If only one OCR engine (e.g. RapidOCR) is available on a scanned document without a digital text layer, the tokens used to verify a field come from the exact same model that proposed it. In VeriDocs AI, same-source evidence is strictly barred from upgrading a field to *Supported*. The field is flagged as *Uncertain* with an explicit explanation in the UI and report.

### Q3: How do you prevent adversarial prompt injection embedded in uploaded PDFs?
**Answer**: Extracted document text is never interpolated into executable prompts, system templates, or shell arguments; it is strictly quarantined as data values inside Pydantic schemas. Additionally, `backend/app/verification/injection_hygiene.py` scans for instruction-like keywords (e.g., 'ignore previous instructions', 'system prompt:'), logs an informational security check, and isolates the payload.

### Q4: How does your bank statement continuity check work?
**Answer**: It iterates sequentially across all extracted transaction rows, verifying $B_i = B_{i-1} + C_i - D_i$ within an absolute tolerance of 0.05. If a discrepancy occurs, it immediately pinpoints the exact first row of the break, reporting the previous balance, the credit/debit, the expected balance, and the actual printed balance.

### Q5: How do you handle Indian numbering systems (lakhs/crores) versus Western notation?
**Answer**: In `normalizers.py`, we detect currency markers ('₹', 'Rs.', 'INR') and parse comma patterns. Indian formatting places the first comma after three digits and subsequent commas every two digits (e.g., `12,34,567.89`). Our normalizer inspects the position of dots and commas, removes thousands/lakh separators, and converts bracket notation `(1,500.00)` into negative floats `-1500.00`.

### Q6: How do you prevent data leakage between your training and test splits?
**Answer**: Our synthetic generator enforces split separation by layout family and by entity identifier. Layouts 1 and 2 are restricted to the Seen (development) split; Layouts 3 and 4 are restricted to Unseen (test). No synthetic name, company, or document appears in both sets, which is continuously verified by `eval/tests/test_split_leakage.py`.

### Q7: Why did you avoid PyMuPDF (fitz) despite its popularity?
**Answer**: PyMuPDF is licensed under the GNU Affero General Public License (AGPLv3), which imposes copyleft requirements that are unacceptable in commercial or permissive software distributions. Instead, we used `pypdfium2` (Apache-2.0 / BSD) for rasterization and `pdfplumber` (MIT) for text extraction.

### Q8: How did your pipeline perform on Unseen Layouts during evaluation?
**Answer**: In our evaluation benchmark, unseen layouts revealed an honest drop in heuristic regex extraction recall because alternative wording like 'Total Net Payable' or 'Take-home' was not present in the seen development templates. However, the verification engine correctly caught these missing/inconsistent fields and classified them as Uncertain or Inconsistent rather than silently accepting errors.

### Q9: What happens when an uploaded document has a small date difference between payslip and bank deposit?
**Answer**: In real payroll, bank clearance can take 1 to 5 days. Our cross-document engine (`compare_payslip_and_bank_statement`) evaluates a configurable 7-day disbursement window. If the credit amount matches within this window, it passes as Supported. If there is a minor variance (such as a wire transfer fee under 200 INR), it classifies the finding as Uncertain rather than flagging a false-positive inconsistency.

### Q10: How do you handle resource exhaustion or memory leaks during document processing?
**Answer**: We limit maximum document size to 10 MB and 10 pages, configure Pillow's decompression limit to 25 million pixels to thwart zip bombs, process pages iteratively, and store uploads in temporary session directories that are purged immediately upon session deletion or when their 1-hour TTL expires.
