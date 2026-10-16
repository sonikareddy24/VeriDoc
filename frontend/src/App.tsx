import { useState, useEffect } from 'react';
import {
  Upload,
  FileText,
  FileCheck,
  Shield,
  Download,
  AlertCircle,
  PlayCircle,
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

      // Reconstruct document metadata list from result
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
      setErrorMessage(err.message || 'Error running demo flow.');
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
    <div className="min-h-screen bg-[#060913] text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
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
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center justify-between text-xs text-rose-300 shadow-glow-rose">
            <div className="flex items-center space-x-2.5">
              <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
              <span className="font-medium">{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-rose-400 hover:text-white font-bold ml-4 p-1"
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
              <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl p-5 shadow-2xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                <div className="flex items-center space-x-3.5">
                  <div className="p-3 bg-gradient-to-tr from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 shadow-glow-emerald">
                    <Shield className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-base font-bold text-white tracking-tight">Audit Session Ledger</h2>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-900 border border-slate-800 rounded-md text-slate-400">
                        {sessionId?.slice(0, 8)}...
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Independent OCR token grounding, deterministic arithmetic &amp; cross-checks complete
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center space-x-2 px-3 py-1.5 bg-[#070b14] rounded-xl border border-slate-800/90 text-xs font-mono">
                    <div className="flex items-center space-x-1">
                      <span className="text-emerald-400 font-bold">{analysis.summary.Supported || 0}</span>
                      <span className="text-slate-500 text-[11px] font-sans">Supported</span>
                    </div>
                    <span className="text-slate-700">|</span>
                    <div className="flex items-center space-x-1">
                      <span className="text-rose-400 font-bold">{analysis.summary.Inconsistent || 0}</span>
                      <span className="text-slate-500 text-[11px] font-sans">Inconsistent</span>
                    </div>
                    <span className="text-slate-700">|</span>
                    <div className="flex items-center space-x-1">
                      <span className="text-amber-400 font-bold">{analysis.summary.Uncertain || 0}</span>
                      <span className="text-slate-500 text-[11px] font-sans">Uncertain</span>
                    </div>
                  </div>

                  <a
                    href={`/api/sessions/${sessionId}/report.pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-1.5 bg-slate-850 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs font-semibold text-slate-200 transition-all flex items-center space-x-1.5 shadow-sm hover:border-sky-500/30"
                  >
                    <Download className="w-3.5 h-3.5 text-sky-400" />
                    <span>Audit PDF</span>
                  </a>

                  <a
                    href={`/api/sessions/${sessionId}/report.json`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-1.5 bg-slate-850 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs font-semibold text-slate-200 transition-all flex items-center space-x-1.5 shadow-sm hover:border-indigo-500/30"
                  >
                    <FileText className="w-3.5 h-3.5 text-indigo-400" />
                    <span>JSON Report</span>
                  </a>
                </div>
              </div>
            )}

            {/* Document Workspace Ribbon */}
            <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl p-5 shadow-2xl space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 bg-sky-500/10 border border-sky-500/20 rounded-lg text-sky-400">
                    <FileCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-tight">Financial Document Bundle</h3>
                    <p className="text-xs text-slate-400">
                      {documents.length > 0
                        ? `${documents.length} document(s) uploaded in current audit session`
                        : 'Upload payslips, statements, or invoices for consistency analysis'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <label className="cursor-pointer px-3.5 py-2 bg-slate-850 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs font-semibold text-slate-200 transition-all flex items-center space-x-2 shadow-sm hover:border-sky-500/40">
                    <Upload className="w-3.5 h-3.5 text-sky-400" />
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
                      className="px-4 py-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-sky-500/25 transition-all flex items-center space-x-2 disabled:opacity-50"
                    >
                      {isAnalyzing ? <Cpu className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
                      <span>{isAnalyzing ? 'Analyzing Pipeline...' : 'Run Analysis'}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Uploaded Documents Tabs */}
              {documents.length > 0 ? (
                <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800/80">
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
                        className={`px-3.5 py-2.5 rounded-xl text-xs text-left transition-all flex items-center space-x-2.5 border ${
                          isSelected
                            ? 'bg-gradient-to-r from-sky-500/20 to-blue-500/10 border-sky-500/50 text-white shadow-lg shadow-sky-500/10'
                            : 'bg-[#070b14]/70 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                        }`}
                      >
                        <FileText className={`w-4 h-4 ${isSelected ? 'text-sky-400' : 'text-slate-500'}`} />
                        <div>
                          <div className="font-semibold truncate max-w-[170px]">{doc.original_filename}</div>
                          {res && (
                            <div className="text-[10px] uppercase font-mono text-slate-500 font-medium">
                              {res.doc_type} • {res.page_count} pg
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="border-2 border-dashed border-slate-800/90 rounded-2xl p-10 text-center space-y-3 bg-[#070b14]/40">
                  <div className="w-12 h-12 mx-auto rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mb-2">
                    <Upload className="w-6 h-6" />
                  </div>
                  <h4 className="text-sm font-bold text-white">Upload Financial Documents</h4>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto">
                    Supports payslips, bank statements, tax invoices, and receipts (PDF, PNG, JPEG up to 10 MB).
                  </p>
                  <div className="pt-2">
                    <button
                      onClick={handleRunDemo}
                      disabled={isAnalyzing}
                      className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold text-sky-300 bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 transition-all"
                    >
                      <span>Or launch live synthesized demonstration</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Analysis Results View */}
            {activeDocResult && sessionId && (
              <div className="space-y-6">
                {/* Two Column Layout: Real Interactive Document Viewer (Left) + Table/Inspector (Right) */}
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

      <footer className="border-t border-slate-900 bg-[#060913] py-4 text-center text-xs text-slate-500 font-mono">
        VeriDocs AI • Evidence-First Financial Document Intelligence Research Prototype • Zero Paid APIs • Apache-2.0 / MIT
      </footer>
    </div>
  );
}
