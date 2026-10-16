"""Pydantic schemas for Cross-Document consistency checks."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from backend.app.schemas.common import FieldStatus


class CrossDocumentFinding(BaseModel):
    check_id: str
    rule_name: str
    doc_id_a: str
    doc_name_a: str
    doc_id_b: str
    doc_name_b: str
    status: FieldStatus
    explanation: str
    details: Dict[str, Any] = Field(default_factory=dict)
