import { useState } from 'react';
import {
  ShieldCheck,
  Code2,
  Copy,
  Check,
  Target,
  FileCheck2,
  Cpu,
} from 'lucide-react';
import { ExtractedField, EvidenceToken } from '../types';

interface EvidenceViewerProps {
  fieldName: string | null;
  field: ExtractedField | null;
  evidenceTokens?: EvidenceToken[];
}

export default function EvidenceViewer({
  fieldName,
  field,
  evidenceTokens = [],
}: EvidenceViewerProps) {
  const [viewMode, setViewMode] = useState<'evidence' | 'json'>('evidence');
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyJson = () => {
    if (!field) return;
    navigator.clipboard.writeText(JSON.stringify(field, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 1500);
  };

  if (!fieldName || !field) {
    return (
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-6 shadow-sm flex flex-col items-center justify-center text-center space-y-2 min-h-[260px]">
        <div className="w-10 h-10 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-500 mb-1">
          <Target className="w-5 h-5 text-slate-400" />
        </div>
        <h4 className="text-xs font-semibold text-slate-200">Evidence Grounding Inspector</h4>
        <p className="text-[11px] text-slate-400 max-w-xs">
          Select any field row in the semantic ledger or click a bounding box on the document canvas to view token grounding and deterministic verification proofs.
        </p>
      </div>
    );
  }

  // Find candidate evidence tokens on the same page
  const matchingTokens = evidenceTokens.filter((t) => {
    if (t.page !== (field.page || 1)) return false;
    if (!field.source_text) return false;
    return field.source_text.toLowerCase().includes(t.text.toLowerCase());
  });

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
      {/* Inspector Header */}
      <div className="px-4 py-3 bg-[#161F30] border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-md bg-slate-800 flex items-center justify-center text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-bold text-white">{fieldName}</span>
              <span className="text-[10px] font-mono text-slate-400 bg-[#0B0F17] px-1.5 py-0.5 rounded border border-slate-800">
                Page {field.page || 1}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Independent Grounding Inspector</p>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center space-x-1 bg-[#0B0F17] border border-slate-800 rounded-md p-0.5">
          <button
            onClick={() => setViewMode('evidence')}
            className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
              viewMode === 'evidence'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Audit View
          </button>
          <button
            onClick={() => setViewMode('json')}
            className={`px-2 py-1 rounded text-[11px] font-medium transition-colors flex items-center space-x-1 ${
              viewMode === 'json'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code2 className="w-3 h-3" />
            <span>JSON</span>
          </button>
        </div>
      </div>

      {/* Inspector Body */}
      {viewMode === 'json' ? (
        <div className="p-4 relative">
          <div className="absolute top-6 right-6">
            <button
              onClick={handleCopyJson}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition-colors flex items-center space-x-1 text-[11px]"
              title="Copy JSON"
            >
              {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{isCopied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
          <pre className="font-mono text-[11px] bg-[#0B0F17] p-3 rounded-lg border border-slate-800/80 text-slate-300 overflow-x-auto max-h-[300px]">
            {JSON.stringify(field, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="p-4 space-y-3.5 text-xs">
          {/* Key Metric Blocks */}
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-[#161F30] p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Raw Extracted
              </span>
              <span className="font-mono text-xs font-semibold text-slate-200 truncate block">
                {String(field.value ?? '—')}
              </span>
            </div>

            <div className="bg-[#161F30] p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Normalized Value
              </span>
              <span className="font-mono text-xs font-semibold text-blue-400 truncate block">
                {String(field.normalized_value ?? field.value ?? '—')}
              </span>
            </div>
          </div>

          {/* Audit Metrics */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="bg-[#0B0F17] p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 block">OCR Confidence</span>
              <span className="font-mono text-xs font-bold text-slate-200">
                {field.ocr_confidence !== null && field.ocr_confidence !== undefined
                  ? `${(field.ocr_confidence * 100).toFixed(1)}%`
                  : 'N/A'}
              </span>
            </div>

            <div className="bg-[#0B0F17] p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Extractor</span>
              <span className="font-mono text-xs font-semibold text-slate-300 flex items-center justify-center space-x-1">
                <Cpu className="w-3 h-3 text-slate-400" />
                <span className="truncate max-w-[80px]">{field.extractor || 'RapidOCR'}</span>
              </span>
            </div>

            <div className="bg-[#0B0F17] p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Status</span>
              <span className={`font-mono text-xs font-bold ${
                field.status === 'Supported'
                  ? 'text-emerald-400'
                  : field.status === 'Inconsistent'
                  ? 'text-rose-400'
                  : 'text-amber-400'
              }`}>
                {field.status}
              </span>
            </div>
          </div>

          {/* Normalized BBox */}
          {field.bbox && field.bbox.length === 4 && (
            <div className="bg-[#161F30] p-2.5 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                  Page Coordinates [x0, y0, x1, y1]
                </span>
                <span className="text-[10px] font-mono text-slate-500">Normalized [0, 1]</span>
              </div>
              <div className="font-mono text-[11px] text-slate-300 bg-[#0B0F17] p-1.5 rounded border border-slate-800/80">
                [{field.bbox.map((v) => v.toFixed(3)).join(', ')}]
              </div>
            </div>
          )}

          {/* Audit Rationale */}
          <div className="bg-[#161F30] p-2.5 rounded-lg border border-slate-800 space-y-1">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
              <FileCheck2 className="w-3.5 h-3.5 text-blue-400" />
              <span>Deterministic Audit Rationale</span>
            </span>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              {field.status_reason ||
                'Grounded in independent visual token evidence and validated by deterministic verification rules.'}
            </p>
          </div>

          {/* Matching Tokens Chip List */}
          {matchingTokens.length > 0 && (
            <div className="bg-[#161F30] p-2.5 rounded-lg border border-slate-800 space-y-1.5">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                Corroborating OCR Tokens ({matchingTokens.length})
              </span>
              <div className="flex flex-wrap gap-1">
                {matchingTokens.slice(0, 8).map((tok, i) => (
                  <span
                    key={i}
                    className="px-1.5 py-0.5 rounded bg-[#0B0F17] border border-slate-800 font-mono text-[10px] text-slate-300"
                  >
                    {tok.text}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
