"""Session management, secure temporary storage, and file validation."""

import os
import shutil
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.session import DocumentMetadata
from backend.app.schemas.document import DocumentAnalysisResult
from backend.app.schemas.cross_document import CrossDocumentFinding

# Configure Pillow decompression protection
Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS

ALLOWED_MAGIC_BYTES = {
    b"%PDF": ("application/pdf", ".pdf"),
    b"\x89PNG\r\n\x1a\n": ("image/png", ".png"),
    b"\xff\xd8\xff": ("image/jpeg", ".jpg"),
}


class Session:
    def __init__(self, session_id: str, ttl_seconds: int = settings.SESSION_TTL_SECONDS):
        self.session_id = session_id
        self.created_at = datetime.now(timezone.utc)
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
        self.storage_dir = settings.TEMP_STORAGE_DIR / session_id
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.documents: Dict[str, DocumentMetadata] = {}
        self.analysis_results: Dict[str, DocumentAnalysisResult] = {}
        self.cross_document_findings: List[CrossDocumentFinding] = []
        self.is_analyzed = False

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def cleanup(self):
        """Remove temporary directory on disk."""
        if self.storage_dir.exists():
            shutil.rmtree(self.storage_dir, ignore_errors=True)


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        settings.TEMP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> Session:
        self.purge_expired()
        session_id = str(uuid.uuid4())
        session = Session(session_id)
        self._sessions[session_id] = session
        logger.info(f"Created new session", extra={"session_id": session_id})
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        self.purge_expired()
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            self.delete_session(session_id)
            return None
        return session

    def delete_session(self, session_id: str) -> bool:
        session = self._sessions.pop(session_id, None)
        if session:
            session.cleanup()
            logger.info(f"Purged session storage", extra={"session_id": session_id})
            return True
        return False

    def purge_expired(self):
        expired = [s_id for s_id, s in self._sessions.items() if s.is_expired()]
        for s_id in expired:
            self.delete_session(s_id)

    @staticmethod
    def validate_and_save_upload(session: Session, original_filename: str, file_bytes: bytes) -> DocumentMetadata:
        """Validate file size and magic bytes, save using a secure random filename."""
        if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds maximum allowed {settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB")

        # Magic byte detection
        detected_mime = None
        safe_extension = None
        for magic, (mime, ext) in ALLOWED_MAGIC_BYTES.items():
            if file_bytes.startswith(magic):
                detected_mime = mime
                safe_extension = ext
                break

        if not detected_mime:
            raise ValueError("Unsupported file type. Only standard PDF, PNG, and JPEG files are permitted.")

        # Check page count if PDF
        if detected_mime == "application/pdf":
            import pypdfium2 as pdfium
            try:
                pdf = pdfium.PdfDocument(file_bytes)
                page_count = len(pdf)
                if page_count > settings.MAX_PAGES_PER_DOC:
                    raise ValueError(f"Document has {page_count} pages; maximum allowed is {settings.MAX_PAGES_PER_DOC} pages.")
            except Exception as e:
                if "maximum allowed" in str(e):
                    raise
                raise ValueError("Corrupt or password-protected PDF document.")

        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}{safe_extension}"
        target_path = session.storage_dir / safe_filename

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        metadata = DocumentMetadata(
            doc_id=doc_id,
            original_filename=Path(original_filename).name,  # Sanitize name
            stored_path=str(target_path),
            content_type=detected_mime,
            size_bytes=len(file_bytes),
            created_at=datetime.now(timezone.utc),
            processed=False,
        )
        session.documents[doc_id] = metadata
        return metadata


session_manager = SessionManager()
