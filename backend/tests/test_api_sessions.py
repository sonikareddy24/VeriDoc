"""Integration tests for Session and Document Analysis API."""

import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.reporting.sample_generator import create_demo_payslip

client = TestClient(app)


def test_session_lifecycle_and_upload():
    # 1. Create session
    resp = client.post("/api/sessions")
    assert resp.status_code == 201
    data = resp.json()
    session_id = data["session_id"]
    assert session_id

    # 2. Upload sample PDF
    pdf_bytes = create_demo_payslip()
    files = {"file": ("test_payslip.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    resp_upload = client.post(f"/api/sessions/{session_id}/documents", files=files)
    assert resp_upload.status_code == 200
    doc_meta = resp_upload.json()
    assert doc_meta["original_filename"] == "test_payslip.pdf"
    assert doc_meta["content_type"] == "application/pdf"

    # 3. Analyze session
    resp_analyze = client.post(f"/api/sessions/{session_id}/analyze")
    assert resp_analyze.status_code == 200
    analysis = resp_analyze.json()
    assert analysis["session_id"] == session_id
    assert len(analysis["documents"]) == 1

    # 4. Get report PDF
    resp_pdf = client.get(f"/api/sessions/{session_id}/report.pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert len(resp_pdf.content) > 1000

    # 5. Delete session
    resp_del = client.delete(f"/api/sessions/{session_id}")
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "deleted"

    # 6. Verify 404 after deletion
    resp_check = client.get(f"/api/sessions/{session_id}")
    assert resp_check.status_code == 404


def test_demo_session_endpoint():
    resp = client.post("/api/demo/session")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert len(data["documents"]) == 2
    # Verify cross-document findings are populated
    assert len(data["cross_document_findings"]) > 0
