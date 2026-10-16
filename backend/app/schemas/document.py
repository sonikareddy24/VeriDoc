"""Document result and metadata schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.common import (
    DocumentType,
    EvidenceToken,
    ExtractedField,
    ImageQualityReport,
    ReviewCategory,
    VerificationCheck,
)


class DocumentAnalysisResult(BaseModel):
    doc_id: str
    filename: str
    doc_type: DocumentType
    page_count: int
    quality: ImageQualityReport
    fields: Dict[str, ExtractedField] = Field(default_factory=dict)
    structured_data: Optional[Dict[str, Any]] = None
    checks: List[VerificationCheck] = Field(default_factory=list)
    review_categories: List[ReviewCategory] = Field(default_factory=list)
    evidence_tokens: List[EvidenceToken] = Field(default_factory=list)
    field_counts: Dict[str, int] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
