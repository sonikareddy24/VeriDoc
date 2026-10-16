# VeriDocs AI — REST API Reference

The VeriDocs AI backend provides a RESTful ASGI interface built with FastAPI. All endpoints accept and emit JSON, with multipart support for document uploads and binary streaming for audit PDF generation.

---

## Base URL & OpenAPI Specification
- Default Local Address: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 1. System & Discovery

### `GET /api/health`
Checks backend operational status.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "VeriDocs AI",
  "version": "0.1.0",
  "timestamp": "2026-10-16T14:49:48.803294+00:00",
  "environment": "development"
}
```

### `GET /api/config`
Discovers active extraction engine, evidence grounders, and system limits.
- **Response `200 OK`**:
```json
{
  "active_extractor_backend": "ocr_rules",
  "ocr_engine": "rapidocr",
  "limits": {
    "max_file_size_bytes": 10485760,
    "max_file_size_mb": 10,
    "max_pages_per_doc": 10,
    "session_ttl_seconds": 3600
  },
  "fuzzy_match_threshold": 85.0,
  "supported_mime_types": ["application/pdf", "image/png", "image/jpeg"]
}
```

### `GET /api/experiments`
Fetches research benchmark evaluation metrics from `results/latest_metrics.json`.

---

## 2. Session Lifecycle & Uploads

### `POST /api/sessions`
Initializes a new ephemeral audit session and creates an isolated temp directory.
- **Response `201 Created`**:
```json
{
  "session_id": "c1f7a0b3-9c8d-4e2b-a1b2-3c4d5e6f7a8b",
  "created_at": "2026-10-16T15:00:00Z",
  "expires_at": "2026-10-16T16:00:00Z"
}
```

### `DELETE /api/sessions/{session_id}`
Immediately deletes session state and purges all uploaded files from disk.
- **Response `200 OK`**:
```json
{
  "status": "deleted",
  "session_id": "c1f7a0b3-9c8d-4e2b-a1b2-3c4d5e6f7a8b"
}
```

### `POST /api/sessions/{session_id}/documents`
Uploads a document (PDF, PNG, JPEG). Validates magic bytes, enforces 10 MB and 10-page limits, and assigns a server-side random UUID filename.
- **Form Data**: `file: Binary`
- **Response `200 OK`**:
```json
{
  "doc_id": "f8a920b1-4c23-49d8-9128-d7e6f5a4b3c2",
  "original_filename": "march_payslip.pdf",
  "stored_path": "/path/to/data/sessions_temp/.../f8a920b1.pdf",
  "content_type": "application/pdf",
  "size_bytes": 48201,
  "created_at": "2026-10-16T15:01:00Z",
  "processed": false
}
```

---

## 3. Analysis & Verification

### `POST /api/sessions/{session_id}/analyze`
Executes extraction pipeline, deterministic verification checks, and cross-document reconciliation.
- **Response `200 OK`**: `SessionAnalysisResponse`
```json
{
  "session_id": "c1f7a0b3-9c8d-4e2b-a1b2-3c4d5e6f7a8b",
  "documents": {
    "doc_1": {
      "doc_id": "doc_1",
      "filename": "march_payslip.pdf",
      "doc_type": "payslip",
      "page_count": 1,
      "quality": {
        "blur_score": 150.0,
        "is_blurry": false,
        "skew_angle_deg": 0.0,
        "warnings": []
      },
      "fields": {
        "net_salary": {
          "name": "net_salary",
          "value": "75,000.00",
          "normalized_value": 75000.0,
          "status": "Supported",
          "status_reason": "Grounded in independent evidence and passed all applicable deterministic checks.",
          "page": 1,
          "bbox": [0.1, 0.45, 0.4, 0.48],
          "extractor": "ocr_rules",
          "ocr_confidence": 0.94
        }
      },
      "checks": [
        {
          "check_id": "PAYSLIP_NET_ARITHMETIC",
          "applies": true,
          "status": "passed",
          "plain_explanation": "Net salary (75000.00) equals gross (85000.00) minus deductions (10000.00).",
          "independence": "independent"
        }
      ],
      "field_counts": {
        "Supported": 6,
        "Inconsistent": 0,
        "Uncertain": 1,
        "Unreadable": 0
      }
    }
  },
  "cross_document_findings": [
    {
      "check_id": "CROSS_SALARY_BANK_CREDIT",
      "rule_name": "Net Salary to Bank Credit Reconciliation",
      "status": "Supported",
      "explanation": "Exact net salary match found! Bank credit of 75000.00 on 2024-03-31 matches payslip."
    }
  ],
  "summary": {
    "Supported": 6,
    "Inconsistent": 0,
    "Uncertain": 1,
    "Unreadable": 0
  }
}
```

### `GET /api/sessions/{session_id}/report.pdf`
Generates and downloads the audit-ready ReportLab PDF report.
- **Response `200 OK`**: Binary `application/pdf` stream.

### `POST /api/demo/session`
Synthesizes a sample demonstration bundle (payslip + bank statement), runs the full real pipeline, and returns the analyzed session.
