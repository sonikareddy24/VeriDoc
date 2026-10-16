"""Pydantic schemas for Invoice and Receipt documents."""

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.common import ExtractedField


class InvoiceLineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    line_total: float = 0.0


class InvoiceData(BaseModel):
    merchant_name: Optional[ExtractedField] = None
    invoice_number: Optional[ExtractedField] = None
    invoice_date: Optional[ExtractedField] = None
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    subtotal: Optional[ExtractedField] = None
    tax: Optional[ExtractedField] = None
    tax_rate: Optional[ExtractedField] = None
    discounts: Optional[ExtractedField] = None
    total: Optional[ExtractedField] = None
    currency: Optional[ExtractedField] = None
