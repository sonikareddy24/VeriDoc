"""Pluggable Extractor Pipeline supporting B1 (OCR + Rules) and B2/B3 (VLM / LoRA predictions)."""

import time
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.common import (
    DocumentType,
    EvidenceToken,
    ExtractedField,
    FieldStatus,
    ImageQualityReport,
    NullReason,
)
from backend.app.schemas.document import DocumentAnalysisResult
from backend.app.extraction.ocr_engine import ocr_engine
from backend.app.extraction.layout_parser import (
    group_tokens_into_lines,
    classify_document,
    parse_payslip,
    parse_bank_statement,
    parse_invoice,
)


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str, mime_type: str, doc_id: str, filename: str) -> DocumentAnalysisResult:
        pass


class OCRRulesExtractor(BaseExtractor):
    """B1: Real OCR (RapidOCR + pdfplumber) with layout-aware heuristic reconstruction."""

    def extract(self, file_path: str, mime_type: str, doc_id: str, filename: str) -> DocumentAnalysisResult:
        start_time = time.perf_counter()

        # 1. OCR Token and Image Extraction
        page_images, tokens, warnings = ocr_engine.render_and_extract_tokens(
            file_path, mime_type, save_dir=Path(file_path).parent, doc_id=doc_id
        )
        page_count = max(1, len(page_images))

        # 2. Quality Report
        quality = ImageQualityReport(
            blur_score=150.0,
            is_blurry=any("blurry" in w.lower() for w in warnings),
            skew_angle_deg=0.0,
            warnings=warnings,
        )

        # 3. Line Reconstruction & Classification
        lines = group_tokens_into_lines(tokens)
        doc_type = classify_document(lines)

        # 4. Domain Parsing
        fields: Dict[str, ExtractedField] = {}
        structured_data = None

        if doc_type == DocumentType.PAYSLIP:
            fields, p_data = parse_payslip(lines)
            structured_data = p_data.model_dump()
        elif doc_type == DocumentType.BANK_STATEMENT:
            fields, b_data = parse_bank_statement(lines)
            structured_data = b_data.model_dump()
        elif doc_type in (DocumentType.INVOICE, DocumentType.RECEIPT):
            fields, i_data = parse_invoice(lines)
            structured_data = i_data.model_dump()
        else:
            # Unknown document type
            warnings.append("Document type could not be confidently identified; generic parsing applied.")

        # Compute counts
        counts = {
            FieldStatus.SUPPORTED.value: sum(1 for f in fields.values() if f.status == FieldStatus.SUPPORTED),
            FieldStatus.INCONSISTENT.value: sum(1 for f in fields.values() if f.status == FieldStatus.INCONSISTENT),
            FieldStatus.UNCERTAIN.value: sum(1 for f in fields.values() if f.status == FieldStatus.UNCERTAIN),
            FieldStatus.UNREADABLE.value: sum(1 for f in fields.values() if f.status == FieldStatus.UNREADABLE),
        }

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return DocumentAnalysisResult(
            doc_id=doc_id,
            filename=filename,
            doc_type=doc_type,
            page_count=page_count,
            quality=quality,
            fields=fields,
            structured_data=structured_data,
            checks=[],  # Populated in verification stage
            review_categories=[],
            evidence_tokens=tokens,
            field_counts=counts,
            execution_time_ms=duration_ms,
        )


class VLMPredictionExtractor(BaseExtractor):
    """B2/B3: Ingests precomputed VLM predictions from Google Colab / GPU runs conforming to schema."""

    def __init__(self, predictions_dir: Optional[Path] = None):
        self.predictions_dir = predictions_dir or (settings.BASE_DIR / "data" / "predictions")

    def extract(self, file_path: str, mime_type: str, doc_id: str, filename: str) -> DocumentAnalysisResult:
        stem = Path(file_path).stem
        pred_file = self.predictions_dir / f"{stem}.json"
        alt_pred_file = self.predictions_dir / f"{doc_id}.json"

        target_file = pred_file if pred_file.exists() else (alt_pred_file if alt_pred_file.exists() else None)

        if target_file and target_file.exists():
            with open(target_file, "r") as f:
                data = json.load(f)
            # Reconstruct DocumentAnalysisResult from loaded prediction
            res = DocumentAnalysisResult(**data)
            res.doc_id = doc_id
            res.filename = filename
            return res
        else:
            # Fallback to OCR rules if no precomputed VLM file exists, with warning
            logger.warning(
                f"No precomputed VLM prediction found at {pred_file}. Falling back to default OCR Rules engine."
            )
            fallback = OCRRulesExtractor()
            result = fallback.extract(file_path, mime_type, doc_id, filename)
            result.quality.warnings.append(
                f"VLM prediction file '{stem}.json' not found in data/predictions/. Ran CPU OCR rules fallback."
            )
            return result


def get_extractor(backend_name: Optional[str] = None) -> BaseExtractor:
    backend = backend_name or settings.DEFAULT_EXTRACTOR_BACKEND
    if backend == "ocr_rules":
        return OCRRulesExtractor()
    elif backend in ("vlm_zero_shot", "vlm_lora"):
        return VLMPredictionExtractor()
    return OCRRulesExtractor()
