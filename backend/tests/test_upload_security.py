"""Unit tests for upload security: magic byte validation, oversize rejection,
path-traversal protection, and session cleanup.
"""

import io
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.sessions.manager import session_manager
from backend.app.core.config import settings

client = TestClient(app)


def test_upload_spoofed_extension_rejection():
    # File named "innocent.pdf" but containing fake plain text bytes (not %PDF magic bytes)
    resp_s = client.post("/api/sessions")
    session_id = resp_s.json()["session_id"]

    spoofed_bytes = b"This is not a real PDF file but has .pdf extension."
    files = {"file": ("innocent.pdf", io.BytesIO(spoofed_bytes), "application/pdf")}
    resp = client.post(f"/api/sessions/{session_id}/documents", files=files)

    assert resp.status_code == 400
    assert "Unsupported file type" in resp.json()["detail"]


def test_upload_oversize_rejection():
    resp_s = client.post("/api/sessions")
    session_id = resp_s.json()["session_id"]

    # Generate oversized dummy payload > 10MB starting with %PDF
    oversized = b"%PDF-1.4 " + b"0" * (11 * 1024 * 1024)
    files = {"file": ("huge.pdf", io.BytesIO(oversized), "application/pdf")}
    resp = client.post(f"/api/sessions/{session_id}/documents", files=files)

    assert resp.status_code == 400
    assert "exceeds maximum allowed" in resp.json()["detail"]


def test_upload_path_traversal_sanitization():
    resp_s = client.post("/api/sessions")
    session_id = resp_s.json()["session_id"]

    # Minimal valid PNG magic bytes + IHDR chunk
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    malicious_filename = "../../../../../etc/passwd.png"

    files = {"file": (malicious_filename, io.BytesIO(png_bytes), "image/png")}
    resp = client.post(f"/api/sessions/{session_id}/documents", files=files)

    assert resp.status_code == 200
    doc_meta = resp_s = resp.json()
    stored_path = Path(doc_meta["stored_path"])

    # Verify target file is strictly inside session storage directory, not in root/etc
    session_dir = settings.TEMP_STORAGE_DIR / session_id
    assert stored_path.parent.resolve() == session_dir.resolve()
    assert "passwd" not in stored_path.name  # Uses server-side UUID


def test_session_cleanup_removes_temp_files():
    resp_s = client.post("/api/sessions")
    session_id = resp_s.json()["session_id"]
    session_dir = settings.TEMP_STORAGE_DIR / session_id
    assert session_dir.exists()

    # Upload file
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    files = {"file": ("test.png", io.BytesIO(png_bytes), "image/png")}
    client.post(f"/api/sessions/{session_id}/documents", files=files)

    # Delete session
    client.delete(f"/api/sessions/{session_id}")
    assert not session_dir.exists()
