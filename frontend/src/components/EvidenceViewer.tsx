import { useState } from 'react';
import {
  ShieldCheck,
  MapPin,
  Search,
  Layers,
  Copy,
  Check,
  Code2,
  FileText,
  AlertTriangle,
} from 'lucide-react';
import { ExtractedField, EvidenceToken } from '../types';

interface EvidenceViewerProps {
  fieldName: string | null;
  field: ExtractedField | null;
  evidenceTokens: EvidenceToken[];
}

export default function EvidenceViewer({ fieldName, field, evidenceTokens }: EvidenceViewerProps) {
  const [copied, setCopied] = useState(false);
  const [showJson, setShowJson] = useState(false);

  if (!fieldName || !field) {
    return (
      <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl p-8 flex flex-col items-center justify-center text-center text-slate-500 h-full min-h-[360px] shadow-2xl">
        <div className="p-3 bg-slate-900 border border-slate-800 rounded-2xl mb-3 text-slate-600">
          <Search className="w-8 h-8" />
        </div>
        <h4 className="text-sm font-bold text-slate-200">Evidence Grounding Inspector</h4>
        <p className="text-xs text-slate-400 max-w-xs mt-1.5 leading-relaxed">
          Select any field in the table or click a bounding box on the document canvas to inspect independent tokens &amp; audit rationale.
        </p>
      </div>
    );
  }

  const bbox = field.bbox;
  const matchedTokens = evidenceTokens.filter((t) => {
    if (!field.normalized_value) return false;
    const target = String(field.normalized_value).toLowerCase();
    const token = t.text.toLowerCase();
    return token.includes(target) || target.includes(token);
  });

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const isSupported = field.status === 'Supported';
  const isInconsistent = field.status === 'Inconsistent';
  const isUncertain = field.status === 'Uncertain';

  return (
    <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl p-5 flex flex-col space-y-4 shadow-2xl">
      {/* Inspector Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-xl text-sky-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white capitalize">{fieldName.replace(/_/g, ' ')}</h4>
            <span className="text-[10px] text-slate-400 font-mono">Independent Grounding Inspector</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowJson(!showJson)}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 text-xs flex items-center space-x-1"
            title="Toggle JSON Schema View"
          >
            <Code2 className="w-3.5 h-3.5" />
          </button>

          <span
            className={`text-[10px] px-2.5 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
              isSupported
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                : isInconsistent
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
            }`}
          >
            {field.status}
          </span>
        </div>
      </div>

      {showJson ? (
        <pre className="bg-[#060913] p-3 rounded-xl border border-slate-800 text-[11px] font-mono text-sky-300 overflow-x-auto max-h-56">
          {JSON.stringify(field, null, 2)}
        </pre>
      ) : (
        <>
          {/* Values Grid */}
          <div className="grid grid-cols-2 gap-3 text-xs bg-[#070b14]/90 p-3 rounded-xl border border-slate-800/80 font-mono relative">
            <div>
              <span className="text-slate-500 block text-[10px] font-sans font-medium uppercase tracking-wider">
                Raw Extracted:
              </span>
              <span className="text-slate-200 font-medium truncate block mt-0.5">
                {String(field.value ?? 'null')}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] font-sans font-medium uppercase tracking-wider">
                Normalized Value:
              </span>
              <span className="text-sky-400 font-bold truncate block mt-0.5">
                {String(field.normalized_value ?? 'null')}
              </span>
            </div>
            <button
              onClick={() => handleCopy(String(field.normalized_value ?? field.value))}
              className="absolute top-2 right-2 p-1 text-slate-500 hover:text-slate-300"
              title="Copy normalized value"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>

          {/* Audit Explanation */}
          <div className="text-xs bg-[#0d1629]/60 p-3 rounded-xl border border-slate-800/70 space-y-1">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 font-semibold flex items-center space-x-1">
                <FileText className="w-3.5 h-3.5 text-sky-400" />
                <span>Deterministic Audit Rationale:</span>
              </span>
              {isUncertain && (
                <span className="inline-flex items-center space-x-1 text-[10px] text-amber-400 bg-amber-500/10 px-1.5 py-0.2 rounded border border-amber-500/20 font-medium">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Same-Source Only</span>
                </span>
              )}
            </div>
            <p className="text-slate-300 text-[11px] leading-relaxed pt-0.5">
              {field.status_reason ||
                'Grounded in independent evidence and verified against deterministic accounting invariants.'}
            </p>
          </div>

          {/* Spatial Coordinates Pill */}
          {bbox && (
            <div className="flex items-center justify-between text-[11px] bg-[#070b14]/70 px-3 py-2 rounded-lg border border-slate-800/80">
              <span className="flex items-center space-x-1 text-slate-400 font-medium">
                <MapPin className="w-3.5 h-3.5 text-sky-400" />
                <span>Page {field.page || 1} Coordinates:</span>
              </span>
              <span className="font-mono text-[10px] text-sky-400 font-semibold bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
                [{bbox.map((v) => v.toFixed(3)).join(', ')}]
              </span>
            </div>
          )}

          {/* Evidence Tokens */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center space-x-1.5 font-semibold text-[11px] text-slate-300">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                <span>Independent Tokens Found ({matchedTokens.length})</span>
              </span>
            </div>

            {matchedTokens.length > 0 ? (
              <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                {matchedTokens.map((t, idx) => (
                  <div
                    key={idx}
                    className="text-[11px] font-mono bg-[#070b14] p-2.5 rounded-lg border border-slate-800/80 flex items-center justify-between text-slate-200"
                  >
                    <span className="truncate max-w-[200px] text-slate-300">&quot;{t.text}&quot;</span>
                    <div className="flex items-center space-x-1.5">
                      {t.confidence !== undefined && (
                        <span className="text-[10px] text-slate-400 font-mono">
                          {(t.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      <span className="text-[9px] text-indigo-400 uppercase font-semibold bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                        {t.source}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-[11px] text-slate-500 italic bg-[#070b14]/50 p-2.5 rounded-lg border border-slate-800/60">
                No secondary token confirmations located on digital vector layers.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
