# VeriDocs AI — System Architecture & Technical Specifications

VeriDocs AI is an evidence-grounded financial document intelligence and consistency verification system. It operates on the foundational principle:
> **Core Axiom:** *An AI model must never be trusted to verify its own output. Extraction proposes; independent deterministic code decides.*

---

## 1. System Architecture Diagram

```mermaid
graph TD
    Client["Client Browser (React + TypeScript + Tailwind)"] -->|"Multipart Upload / REST API"| API["FastAPI Application (backend/app/main.py)"]
    
    subgraph Storage & Session Isolation
        SessionMgr["Session Manager (backend/app/sessions/manager.py)"]
        TempDisk["Ephemeral Temp Disk (Per-Session UUID / TTL 1h)"]
        SessionMgr --> TempDisk
    end
    API --> SessionMgr

    subgraph Extraction Pipeline [backend/app/extraction/]
        QualityGate["Quality Gate (cv2 Laplacian blur + Auto-Deskew)"]
        PDFRasterizer["pypdfium2 (PDF -> 200 DPI BGR Bitmaps)"]
        DigitalText["pdfplumber (Digital Text Layer & Word BBoxes)"]
        OpticalOCR["RapidOCR ONNX (Optical Character Recognition)"]
        LayoutParser["Layout-Aware Heuristic Parser (Payslip / Bank / Invoice)"]
        
        QualityGate --> PDFRasterizer
        PDFRasterizer --> OpticalOCR
        PDFRasterizer --> DigitalText
        OpticalOCR --> LayoutParser
        DigitalText --> LayoutParser
    end
    API --> QualityGate

    subgraph Verification Engine [backend/app/verification/]
        Grounding["Evidence Grounding Check (Token matching + BBox proximity)"]
        FormatPlausibility["Format & Plausibility Validation"]
        Arithmetic["Deterministic Arithmetic Engine (Gross/Net/Subtotal)"]
        Continuity["Bank Statement Running Balance Continuity Chaining"]
        Hygiene["Prompt Injection Sanitization & Data Quarantining"]
        StatusResolver["Status Model Aggregator (Supported / Inconsistent / Uncertain / Unreadable)"]

        Grounding --> StatusResolver
        FormatPlausibility --> StatusResolver
        Arithmetic --> StatusResolver
        Continuity --> StatusResolver
        Hygiene --> StatusResolver
    end
    LayoutParser --> VerificationEngine

    subgraph Multi-Document Reconciliation
        CrossDoc["Cross-Document Reconciler (Payslip Net vs Bank Credit & Timing)"]
    end
    StatusResolver --> CrossDoc

    subgraph Reporting Layer [backend/app/reporting/]
        PDFReport["ReportLab PDF Generator (Audit-Ready PDF)"]
        JSONReport["JSON Session Analysis Response"]
    end
    CrossDoc --> PDFReport
    CrossDoc --> JSONReport
    PDFReport --> Client
    JSONReport --> Client
```

---

## 2. End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Client / Browser
    participant API as FastAPI Router
    participant Session as Session Storage
    participant Gate as Quality Gate & Deskew
    participant OCR as Dual Reader (pdfplumber + RapidOCR)
    participant Parser as Layout Parser
    participant Engine as Verification Engine
    participant Cross as Cross-Doc Reconciler
    participant Report as ReportLab Generator

    User->>API: POST /api/sessions
    API-->>User: session_id, expires_at

    User->>API: POST /api/sessions/{id}/documents (Files)
    API->>Session: Validate Magic Bytes (%PDF, PNG, JPEG) & Size
    Session->>Session: Store with Server-Side Random UUID
    API-->>User: DocumentMetadata (doc_id)

    User->>API: POST /api/sessions/{id}/analyze
    API->>Gate: Assess Laplacian Blur & Skew
    Gate-->>API: Deskewed Image + Quality Warnings
    API->>OCR: Render Pages & Extract Digital + Visual Tokens
    OCR-->>API: Normalized Evidence Tokens [x0, y0, x1, y1]
    API->>Parser: Classify & Extract Fields (ocr_rules)
    Parser-->>API: ExtractedField Objects (Status: Uncertain)
    
    API->>Engine: Run Grounding, Arithmetic, Continuity, Hygiene
    Engine-->>API: VerificationChecks & Field Status Aggregation
    
    API->>Cross: Compare Payslip & Bank Statement
    Cross-->>API: CrossDocumentFindings (Benign Differences -> Uncertain)
    
    API-->>User: SessionAnalysisResponse (JSON)

    User->>API: GET /api/sessions/{id}/report.pdf
    API->>Report: Build PDF with Tables, Warnings & Checks
    Report-->>User: application/pdf Stream
```

---

## 3. Privacy, Security & Resource Boundaries

1. **Untrusted Data Isolation**: All text extracted from documents is treated exclusively as untrusted data payloads inside schema objects. Text is never concatenated into shell commands, system calls, or unescaped model prompts.
2. **Privacy-Preserving Logs**: Structured logs record only session UUIDs, document types, processing latencies, and status counts. Document contents, names, salaries, and account numbers are strictly excluded from logs.
3. **Decompression Bomb Protection**: Pillow's `MAX_IMAGE_PIXELS` is strictly clamped to 25 megapixels to prevent zip-bomb / pixel-flood memory denial-of-service attacks.
4. **Per-Session TTL Cleanup**: Uploaded files reside in `data/sessions_temp/{session_id}`. Deleting a session via `DELETE /api/sessions/{id}` immediately purges all files from disk. Expired sessions are automatically cleared by TTL sweepers.
5. **Permissive Licensing**: The system uses zero AGPL/copyleft dependencies, relying on Apache-2.0 (`pypdfium2`, `RapidOCR`, `OpenCV`), MIT (`pdfplumber`, `FastAPI`, `Pydantic`, `RapidFuzz`), and BSD-3-Clause (`ReportLab`, `NumPy`, `SciPy`).
