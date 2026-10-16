"""Pydantic schemas for Bank Statement documents."""

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.common import ExtractedField


class BankTransaction(BaseModel):
    row_idx: int
    date: Optional[str] = None
    description: str = ""
    debit: Optional[float] = None
    credit: Optional[float] = None
    running_balance: Optional[float] = None
    raw_text: str = ""


class BankStatementData(BaseModel):
    account_holder_name: Optional[ExtractedField] = None
    statement_period_start: Optional[ExtractedField] = None
    statement_period_end: Optional[ExtractedField] = None
    opening_balance: Optional[ExtractedField] = None
    closing_balance: Optional[ExtractedField] = None
    currency: Optional[ExtractedField] = None
    transactions: List[BankTransaction] = Field(default_factory=list)
