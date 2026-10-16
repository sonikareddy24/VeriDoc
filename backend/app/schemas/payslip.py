"""Pydantic schemas for Payslip documents."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.common import ExtractedField


class PayslipItem(BaseModel):
    description: str
    amount: float


class PayslipData(BaseModel):
    employee_name: Optional[ExtractedField] = None
    employee_id: Optional[ExtractedField] = None
    employer_name: Optional[ExtractedField] = None
    pay_period_start: Optional[ExtractedField] = None
    pay_period_end: Optional[ExtractedField] = None
    payment_date: Optional[ExtractedField] = None
    basic_salary: Optional[ExtractedField] = None
    allowances: Optional[List[PayslipItem]] = Field(default_factory=list)
    deductions: Optional[List[PayslipItem]] = Field(default_factory=list)
    total_allowances: Optional[ExtractedField] = None
    total_deductions: Optional[ExtractedField] = None
    gross_salary: Optional[ExtractedField] = None
    net_salary: Optional[ExtractedField] = None
    currency: Optional[ExtractedField] = None
