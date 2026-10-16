"""Core schema types and primitives for VeriDocs AI."""

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class FieldStatus(str, Enum):
    SUPPORTED = "Supported"
    INCONSISTENT = "Inconsistent"
    UNCERTAIN = "Uncertain"
    UNREADABLE = "Unreadable"


class NullReason(str, Enum):
    NOT_FOUND = "not_found"
    UNREADABLE = "unreadable"
    AMBIGUOUS = "ambiguous"
    LOW_QUALITY = "low_quality"


class EvidenceIndependence(str, Enum):
    INDEPENDENT = "independent"
    SAME_SOURCE = "same_source"


class ReviewCategory(str, Enum):
    EXTRACTION_ERROR_LIKELY = "extraction_error_likely"
    IMAGE_QUALITY_PROBLEM = "image_quality_problem"
    CONSISTENCY_ISSUE_NEEDS_REVIEW = "consistency_issue_needs_review"


class DocumentType(str, Enum):
    PAYSLIP = "payslip"
    BANK_STATEMENT = "bank_statement"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    UNKNOWN = "unknown"


class ImageQualityReport(BaseModel):
    blur_score: float = Field(..., description="Laplacian variance blur score")
    is_blurry: bool = Field(default=False)
    skew_angle_deg: float = Field(default=0.0, description="Estimated skew angle in degrees")
    resolution_dpi: Optional[int] = Field(default=None)
    warnings: List[str] = Field(default_factory=list)


class ExtractedField(BaseModel):
    name: str
    value: Optional[Any] = None
    normalized_value: Optional[Any] = None
    status: FieldStatus = FieldStatus.UNCERTAIN
    status_reason: Optional[str] = None
    null_reason: Optional[NullReason] = None
    page: Optional[int] = 1
    bbox: Optional[List[float]] = Field(default=None, description="[x0, y0, x1, y1] normalized coords (0-1)")
    source_text: Optional[str] = None
    extractor: str = "ocr_rules"
    ocr_confidence: Optional[float] = Field(
        default=None,
        description="Raw confidence from OCR engine if available (0.0 - 1.0). NOT a correctness probability.",
    )


class VerificationCheck(BaseModel):
    check_id: str
    applies: bool
    applies_reason: Optional[str] = None
    status: str = Field(..., description="'passed', 'failed', or 'indeterminate'")
    evidence_refs: List[str] = Field(default_factory=list)
    plain_explanation: str
    independence: EvidenceIndependence = EvidenceIndependence.SAME_SOURCE


class EvidenceToken(BaseModel):
    text: str
    page: int
    bbox: List[float] = Field(..., description="[x0, y0, x1, y1]")
    confidence: Optional[float] = None
    source: str = "rapidocr"  # "rapidocr" or "pdf_text_layer"
