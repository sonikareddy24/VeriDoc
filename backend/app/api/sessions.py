"""Session management and document verification endpoints."""

import io
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, Response

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.sessions.manager import session_manager
from backend.app.schemas.session import (
    SessionAnalysisResponse,
    SessionCreateResponse,
    SessionDetailResponse,
)
from backend.app.schemas.document import DocumentAnalysisResult
from backend.app.schemas.common import DocumentType, FieldStatus
from backend.app.schemas.cross_document import CrossDocumentFinding
from backend.app.extraction.pipeline import get_extractor
from backend.app.verification.engine import verification_engine
from backend.app.verification.cross_document import compare_payslip_and_bank_statement
from backend.app.reporting.pdf_report import generate_pdf_report
from backend.app.reporting.sample_generator import create_demo_payslip, create_demo_bank_statement

router = APIRouter()


@router.post("/sessions", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_session():
    session = session_manager.create_session()
    return SessionCreateResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        expires_at=session.expires_at,
    )


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or already expired.")
    return {"status": "deleted", "session_id": session_id}


@router.post("/sessions/{session_id}/documents")
async def upload_document(session_id: str, file: UploadFile = File(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    content = await file.read()
    try:
        metadata = session_manager.validate_and_save_upload(
            session=session,
            original_filename=file.filename or "upload.pdf",
            file_bytes=content,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(
        "Document uploaded successfully",
        extra={"session_id": session_id, "doc_id": metadata.doc_id, "size_bytes": metadata.size_bytes},
    )
    return metadata


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session_details(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    summary = {}
    if session.is_analyzed:
        for res in session.analysis_results.values():
            for status_key, cnt in res.field_counts.items():
                summary[status_key] = summary.get(status_key, 0) + cnt

    return SessionDetailResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        expires_at=session.expires_at,
        documents=list(session.documents.values()),
        analyzed=session.is_analyzed,
        summary=summary,
    )


@router.post("/sessions/{session_id}/analyze", response_model=SessionAnalysisResponse)
def analyze_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    if not session.documents:
        raise HTTPException(status_code=400, detail="No documents uploaded in this session.")

    extractor = get_extractor()

    # 1. Extract and verify each document
    for doc_id, meta in session.documents.items():
        if doc_id not in session.analysis_results:
            raw_result = extractor.extract(
                file_path=meta.stored_path,
                mime_type=meta.content_type,
                doc_id=doc_id,
                filename=meta.original_filename,
            )
            verified_result = verification_engine.verify_document(raw_result)
            session.analysis_results[doc_id] = verified_result
            meta.processed = True

    # 2. Cross-document reconciliation
    cross_findings: List[CrossDocumentFinding] = []
    doc_results = list(session.analysis_results.values())

    payslips = [d for d in doc_results if d.doc_type == DocumentType.PAYSLIP]
    banks = [d for d in doc_results if d.doc_type == DocumentType.BANK_STATEMENT]

    for p in payslips:
        for b in banks:
            findings = compare_payslip_and_bank_statement(p, b)
            cross_findings.extend(findings)

    session.cross_document_findings = cross_findings
    session.is_analyzed = True

    # Summary counts
    summary = {
        FieldStatus.SUPPORTED.value: sum(r.field_counts.get(FieldStatus.SUPPORTED.value, 0) for r in doc_results),
        FieldStatus.INCONSISTENT.value: sum(r.field_counts.get(FieldStatus.INCONSISTENT.value, 0) for r in doc_results),
        FieldStatus.UNCERTAIN.value: sum(r.field_counts.get(FieldStatus.UNCERTAIN.value, 0) for r in doc_results),
        FieldStatus.UNREADABLE.value: sum(r.field_counts.get(FieldStatus.UNREADABLE.value, 0) for r in doc_results),
    }

    logger.info(
        "Session analysis completed",
        extra={"session_id": session_id, "status_counts": summary},
    )

    return SessionAnalysisResponse(
        session_id=session_id,
        documents=session.analysis_results,
        cross_document_findings=cross_findings,
        summary=summary,
        analyzed_at=datetime.now(timezone.utc),
    )


@router.get("/sessions/{session_id}/documents/{doc_id}/result", response_model=DocumentAnalysisResult)
def get_document_result(session_id: str, doc_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    result = session.analysis_results.get(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document result not found. Run /analyze first.")

    return result


@router.get("/sessions/{session_id}/report.json", response_model=SessionAnalysisResponse)
def get_report_json(session_id: str):
    session = session_manager.get_session(session_id)
    if not session or not session.is_analyzed:
        raise HTTPException(status_code=404, detail="Session not found or not yet analyzed.")

    summary = {
        FieldStatus.SUPPORTED.value: sum(r.field_counts.get(FieldStatus.SUPPORTED.value, 0) for r in session.analysis_results.values()),
        FieldStatus.INCONSISTENT.value: sum(r.field_counts.get(FieldStatus.INCONSISTENT.value, 0) for r in session.analysis_results.values()),
        FieldStatus.UNCERTAIN.value: sum(r.field_counts.get(FieldStatus.UNCERTAIN.value, 0) for r in session.analysis_results.values()),
        FieldStatus.UNREADABLE.value: sum(r.field_counts.get(FieldStatus.UNREADABLE.value, 0) for r in session.analysis_results.values()),
    }

    return SessionAnalysisResponse(
        session_id=session_id,
        documents=session.analysis_results,
        cross_document_findings=session.cross_document_findings,
        summary=summary,
        analyzed_at=datetime.now(timezone.utc),
    )


@router.get("/sessions/{session_id}/report.pdf")
def get_report_pdf(session_id: str):
    session = session_manager.get_session(session_id)
    if not session or not session.is_analyzed:
        raise HTTPException(status_code=404, detail="Session not found or not yet analyzed.")

    summary = {
        FieldStatus.SUPPORTED.value: sum(r.field_counts.get(FieldStatus.SUPPORTED.value, 0) for r in session.analysis_results.values()),
        FieldStatus.INCONSISTENT.value: sum(r.field_counts.get(FieldStatus.INCONSISTENT.value, 0) for r in session.analysis_results.values()),
        FieldStatus.UNCERTAIN.value: sum(r.field_counts.get(FieldStatus.UNCERTAIN.value, 0) for r in session.analysis_results.values()),
        FieldStatus.UNREADABLE.value: sum(r.field_counts.get(FieldStatus.UNREADABLE.value, 0) for r in session.analysis_results.values()),
    }

    analysis = SessionAnalysisResponse(
        session_id=session_id,
        documents=session.analysis_results,
        cross_document_findings=session.cross_document_findings,
        summary=summary,
        analyzed_at=datetime.now(timezone.utc),
    )

    pdf_bytes = generate_pdf_report(analysis)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=veridocs_report_{session_id[:8]}.pdf"},
    )


@router.post("/demo/session", response_model=SessionAnalysisResponse)
def run_demo_session():
    """Generates synthetic sample documents, runs the REAL extraction and verification pipeline."""
    session = session_manager.create_session()

    # 1. Create genuine synthetic sample documents
    payslip_pdf = create_demo_payslip()
    bank_pdf = create_demo_bank_statement()

    # 2. Upload them to the session
    session_manager.validate_and_save_upload(session, "Demo_Payslip_AmitVerma.pdf", payslip_pdf)
    session_manager.validate_and_save_upload(session, "Demo_BankStatement_AmitVerma.pdf", bank_pdf)

    # 3. Analyze through real pipeline
    return analyze_session(session.session_id)
