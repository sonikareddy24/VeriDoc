import { useState, useEffect } from 'react';
import {
  Upload,
  FileText,
  FileCheck,
  Shield,
  Download,
  AlertCircle,
  Play,
  Cpu,
  ArrowRight,
} from 'lucide-react';
import Navbar from './components/Navbar';
import DisclaimerBanner from './components/DisclaimerBanner';
import FieldTable from './components/FieldTable';
import EvidenceViewer from './components/EvidenceViewer';
import DocumentViewer from './components/DocumentViewer';
import VerificationCard from './components/VerificationCard';
import CrossDocumentCard from './components/CrossDocumentCard';
import ExperimentsView from './components/ExperimentsView';
import { SessionAnalysisResponse, DocumentMetadata } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<'workspace' | 'experiments'>('workspace');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [analysis, setAnalysis] = useState<SessionAnalysisResponse | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initialize session on mount
  useEffect(() => {
    if (!sessionId) {
      fetch('/api/sessions', { method: 'POST' })
        .then((res) => res.json())
        .then((data) => setSessionId(data.session_id))
        .catch(() => setErrorMessage('Unable to connect to VeriDocs backend API.'));
    }
  }, [sessionId]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !sessionId) return;
    setErrorMessage(null);
    setIsUploading(true);

    try {
      for (const file of Array.from(e.target.files)) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`/api/sessions/${sessionId}/documents`, {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || 'Upload failed');
        }

        const meta: DocumentMetadata = await res.json();
        setDocuments((prev) => [...prev, meta]);
        if (!selectedDocId) {
          setSelectedDocId(meta.doc_id);
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error uploading file.');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const handleRunAnalysis = async () => {
    if (!sessionId) return;
    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const res = await fetch(`/api/sessions/${sessionId}/analyze`, { method: 'POST' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Analysis failed');
      }
      const data: SessionAnalysisResponse = await res.json();
      setAnalysis(data);

      const firstDocId = Object.keys(data.documents)[0];
      if (firstDocId) {
        setSelectedDocId(firstDocId);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error analyzing session documents.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRunDemo = async () => {
    setIsAnalyzing(true);
    setErrorMessage(null);
    try {
      const res = await fetch('/api/demo/session', { method: 'POST' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Demo generation failed');
      }
      const data: SessionAnalysisResponse = await res.json();
      setSessionId(data.session_id);
      setAnalysis(data);

      const docList: DocumentMetadata[] = Object.values(data.documents).map((d) => ({
        doc_id: d.doc_id,
        original_filename: d.filename,
        size_bytes: 48000,
        created_at: new Date().toISOString(),
        processed: true,
      }));
      setDocuments(docList);
      const firstDocId = Object.keys(data.documents)[0];
      if (firstDocId) {
        setSelectedDocId(firstDocId);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error running sample scenario.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClearSession = async () => {
    if (sessionId) {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' }).catch(() => {});
    }
    setSessionId(null);
    setDocuments([]);
    setAnalysis(null);
    setSelectedDocId(null);
    setSelectedField(null);
    setErrorMessage(null);

    const res = await fetch('/api/sessions', { method: 'POST' });
    const data = await res.json();
    setSessionId(data.session_id);
  };

  const activeDocResult = selectedDocId && analysis ? analysis.documents[selectedDocId] : null;
  const activeFieldObj =
    activeDocResult && selectedField ? activeDocResult.fields[selectedField] || null : null;

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-200 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunDemo={handleRunDemo}
        onClearSession={handleClearSession}
        isAnalyzing={isAnalyzing}
        hasSession={!!sessionId && (documents.length > 0 || !!analysis)}
      />

      <DisclaimerBanner />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {errorMessage && (
          <div className="mb-6 p-3.5 bg-rose-950/40 border border-rose-800/60 rounded-xl flex items-center justify-between text-xs text-rose-300">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-rose-400 hover:text-white font-semibold ml-4 px-1"
            >
              ✕
            </button>
          </div>
        )}

        {activeTab === 'experiments' ? (
          <ExperimentsView />
        ) : (
          <div className="space-y-6">
            {/* Header summary when analyzed */}
            {analysis && (
              <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
                    <Shield className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-xs font-bold text-white tracking-tight">Audit Session Ledger</h2>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-[#0B0F17] border border-slate-800 rounded text-slate-400">
                        {sessionId?.slice(0, 8)}...
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Independent OCR token grounding, deterministic arithmetic &amp; cross-checks complete
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  <div className="flex items-center space-x-2 px-3 py-1 bg-[#0B0F17] rounded-lg border border-slate-800 text-xs font-mono">
                    <div className="flex items-center space-x-1">
                      <span className="text-emerald-400 font-bold">{analysis.summary.Supported || 0}</span>
                      <span className="text-slate-400 text-[11px] font-sans">Supported</span>
                    </div>
                    <span className="text-slate-700">|</span>
                    <div className="flex items-center space-x-1">
                      <span className="text-rose-400 font-bold">{analysis.summary.Inconsistent || 0}</span>
                      <span className="text-slate-400 text-[11px] font-sans">Inconsistent</span>
                    </div>
                    <span className="text-slate-700">|</span>
                    <div className="flex items-center space-x-1">
                      <span className="text-amber-400 font-bold">{analysis.summary.Uncertain || 0}</span>
                      <span className="text-slate-400 text-[11px] font-sans">Uncertain</span>
                    </div>
                  </div>

                  <a
                    href={`/api/sessions/${sessionId}/report.pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 bg-[#161F30] hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-medium text-slate-200 transition-colors flex items-center space-x-1.5 shadow-xs"
                  >
                    <Download className="w-3.5 h-3.5 text-blue-400" />
                    <span>Audit PDF</span>
                  </a>

                  <a
                    href={`/api/sessions/${sessionId}/report.json`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 bg-[#161F30] hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-medium text-slate-200 transition-colors flex items-center space-x-1.5 shadow-xs"
                  >
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                    <span>JSON Report</span>
                  </a>
                </div>
              </div>
            )}

            {/* Document Workspace Ribbon */}
            <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
                    <FileCheck className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-white tracking-tight">Financial Document Bundle</h3>
                    <p className="text-[11px] text-slate-400">
                      {documents.length > 0
                        ? `${documents.length} document(s) uploaded in current audit session`
                        : 'Upload payslips, statements, or invoices for consistency analysis'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <label className="cursor-pointer px-3 py-1.5 bg-[#161F30] hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-medium text-slate-200 transition-colors flex items-center space-x-1.5 shadow-xs">
                    <Upload className="w-3.5 h-3.5 text-slate-400" />
                    <span>{isUploading ? 'Uploading...' : 'Upload PDF/Images'}</span>
                    <input
                      type="file"
                      multiple
                      accept="application/pdf,image/png,image/jpeg"
                      onChange={handleFileUpload}
                      className="hidden"
                      disabled={isUploading || isAnalyzing}
                    />
                  </label>

                  {documents.length > 0 && !analysis && (
                    <button
                      onClick={handleRunAnalysis}
                      disabled={isAnalyzing}
                      className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1.5 disabled:opacity-50"
                    >
                      {isAnalyzing ? <Cpu className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                      <span>{isAnalyzing ? 'Analyzing Pipeline...' : 'Run Analysis'}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Uploaded Documents Tabs */}
              {documents.length > 0 ? (
                <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800">
                  {documents.map((doc) => {
                    const isSelected = selectedDocId === doc.doc_id;
                    const res = analysis ? analysis.documents[doc.doc_id] : null;

                    return (
                      <button
                        key={doc.doc_id}
                        onClick={() => {
                          setSelectedDocId(doc.doc_id);
                          setSelectedField(null);
                        }}
                        className={`px-3 py-2 rounded-lg text-xs text-left transition-colors flex items-center space-x-2.5 border ${
                          isSelected
                            ? 'bg-blue-600/15 border-blue-500/50 text-white'
                            : 'bg-[#0B0F17] border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                        }`}
                      >
                        <FileText className={`w-4 h-4 ${isSelected ? 'text-blue-400' : 'text-slate-500'}`} />
                        <div>
                          <div className="font-medium truncate max-w-[170px]">{doc.original_filename}</div>
                          {res && (
                            <div className="text-[10px] uppercase font-mono text-slate-500">
                              {res.doc_type} • {res.page_count} pg
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="border border-dashed border-slate-800 rounded-xl p-8 text-center space-y-2.5 bg-[#0B0F17]">
                  <div className="w-10 h-10 mx-auto rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 mb-1">
                    <Upload className="w-5 h-5 text-slate-400" />
                  </div>
                  <h4 className="text-xs font-semibold text-white">Upload Financial Documents</h4>
                  <p className="text-[11px] text-slate-400 max-w-sm mx-auto">
                    Supports payslips, bank statements, tax invoices, and receipts (PDF, PNG, JPEG up to 10 MB).
                  </p>
                  <div className="pt-1">
                    <button
                      onClick={handleRunDemo}
                      disabled={isAnalyzing}
                      className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-blue-400 bg-blue-600/10 hover:bg-blue-600/20 border border-blue-500/30 transition-colors"
                    >
                      <span>Or launch synthesized sample scenario</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Analysis Results View */}
            {activeDocResult && sessionId && (
              <div className="space-y-6">
                {/* Two Column Layout: Document Viewer (Left) + Table/Inspector (Right) */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                  {/* Left Column: Interactive Document Canvas */}
                  <div className="lg:col-span-7">
                    <DocumentViewer
                      sessionId={sessionId}
                      docId={activeDocResult.doc_id}
                      filename={activeDocResult.filename}
                      pageCount={activeDocResult.page_count}
                      fields={activeDocResult.fields}
                      selectedField={selectedField}
                      onSelectField={(f) => setSelectedField(f)}
                    />
                  </div>

                  {/* Right Column: Semantic Table & Evidence Inspector */}
                  <div className="lg:col-span-5 space-y-6">
                    <FieldTable
                      fields={activeDocResult.fields}
                      selectedField={selectedField}
                      onSelectField={(f) => setSelectedField(f)}
                    />

                    <EvidenceViewer
                      fieldName={selectedField}
                      field={activeFieldObj}
                      evidenceTokens={activeDocResult.evidence_tokens}
                    />
                  </div>
                </div>

                {/* Per-Document Deterministic Verification Rules */}
                <VerificationCard checks={activeDocResult.checks} />

                {/* Cross-Document Reconciliation Card */}
                {analysis && analysis.cross_document_findings.length > 0 && (
                  <CrossDocumentCard findings={analysis.cross_document_findings} />
                )}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800/80 bg-[#0E131F] py-3.5 text-center text-[11px] text-slate-500 font-mono">
        VeriDocs AI • Evidence-First Financial Document Intelligence Research Prototype • Zero Paid APIs
      </footer>
    </div>
  );
}
