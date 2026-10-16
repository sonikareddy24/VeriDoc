export type FieldStatus = 'Supported' | 'Inconsistent' | 'Uncertain' | 'Unreadable';

export interface ExtractedField {
  name: string;
  value?: any;
  normalized_value?: any;
  status: FieldStatus;
  status_reason?: string;
  null_reason?: string;
  page?: number;
  bbox?: [number, number, number, number];
  source_text?: string;
  extractor: string;
  ocr_confidence?: number;
}

export interface VerificationCheck {
  check_id: string;
  applies: boolean;
  applies_reason?: string;
  status: 'passed' | 'failed' | 'indeterminate';
  evidence_refs: string[];
  plain_explanation: string;
  independence: 'independent' | 'same_source';
}

export interface EvidenceToken {
  text: string;
  page: number;
  bbox: [number, number, number, number];
  confidence?: number;
  source: string;
}

export interface ImageQualityReport {
  blur_score: number;
  is_blurry: boolean;
  skew_angle_deg: number;
  warnings: string[];
}

export interface DocumentAnalysisResult {
  doc_id: string;
  filename: string;
  doc_type: 'payslip' | 'bank_statement' | 'invoice' | 'receipt' | 'unknown';
  page_count: number;
  quality: ImageQualityReport;
  fields: Record<string, ExtractedField>;
  structured_data?: any;
  checks: VerificationCheck[];
  review_categories: string[];
  evidence_tokens: EvidenceToken[];
  field_counts: Record<string, number>;
  execution_time_ms: number;
}

export interface CrossDocumentFinding {
  check_id: string;
  rule_name: string;
  doc_id_a: string;
  doc_name_a: string;
  doc_id_b: string;
  doc_name_b: string;
  status: FieldStatus;
  explanation: string;
  details: Record<string, any>;
}

export interface SessionAnalysisResponse {
  session_id: string;
  documents: Record<string, DocumentAnalysisResult>;
  cross_document_findings: CrossDocumentFinding[];
  summary: Record<string, number>;
  analyzed_at: string;
}

export interface DocumentMetadata {
  doc_id: string;
  original_filename: string;
  size_bytes: number;
  created_at: string;
  processed: boolean;
}
