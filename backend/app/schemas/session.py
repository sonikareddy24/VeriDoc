"""Session lifecycle and multi-document bundle schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.document import DocumentAnalysisResult
from backend.app.schemas.cross_document import CrossDocumentFinding


class DocumentMetadata(BaseModel):
    doc_id: str
    original_filename: str
    stored_path: str
    content_type: str
    size_bytes: int
    created_at: datetime
    processed: bool = False


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime


class SessionDetailResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime
    documents: List[DocumentMetadata]
    analyzed: bool
    summary: Dict[str, int] = Field(default_factory=dict)


class SessionAnalysisResponse(BaseModel):
    session_id: str
    documents: Dict[str, DocumentAnalysisResult]
    cross_document_findings: List[CrossDocumentFinding]
    summary: Dict[str, int]
    analyzed_at: datetime
