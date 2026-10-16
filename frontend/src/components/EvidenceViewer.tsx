import { ShieldCheck, MapPin, Search, Layers } from 'lucide-react';
import { ExtractedField, EvidenceToken } from '../types';

interface EvidenceViewerProps {
  fieldName: string | null;
  field: ExtractedField | null;
  evidenceTokens: EvidenceToken[];
}

export default function EvidenceViewer({ fieldName, field, evidenceTokens }: EvidenceViewerProps) {
  if (!fieldName || !field) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center text-center text-slate-500 h-full min-h-[320px]">
        <Search className="w-10 h-10 mb-3 text-slate-600" />
        <h4 className="text-sm font-semibold text-slate-300">Evidence Grounding Inspector</h4>
        <p className="text-xs text-slate-500 max-w-xs mt-1">
          Select any extracted field in the table to examine its independent OCR grounding, bounding coordinates, and confidence.
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

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col space-y-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-sky-500/10 border border-sky-500/30 rounded-lg text-sky-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white capitalize">{fieldName.replace(/_/g, ' ')}</h4>
            <span className="text-[10px] text-slate-400 font-mono">Evidence Inspection</span>
          </div>
        </div>
        <span
          className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
            field.status === 'Supported'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
              : field.status === 'Inconsistent'
              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
          }`}
        >
          {field.status}
        </span>
      </div>

      {/* Value & Normalized Value */}
      <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 font-mono">
        <div>
          <span className="text-slate-500 block text-[10px]">Raw Extracted:</span>
          <span className="text-slate-200 font-medium truncate block">{String(field.value ?? 'null')}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px]">Normalized Value:</span>
          <span className="text-sky-400 font-bold truncate block">{String(field.normalized_value ?? 'null')}</span>
        </div>
      </div>

      {/* Explanation */}
      <div className="text-xs bg-slate-800/40 p-3 rounded-lg border border-slate-800">
        <span className="text-slate-400 font-semibold block text-[11px] mb-1">Status Explanation:</span>
        <p className="text-slate-300 text-[11px] leading-relaxed">
          {field.status_reason || 'Verified through independent evidence token grounding and deterministic validation.'}
        </p>
      </div>

      {/* Visual Spatial Box Overlay */}
      {bbox && (
        <div className="border border-slate-800 rounded-lg p-3 bg-slate-950/80 flex flex-col items-center">
          <div className="w-full flex items-center justify-between text-[11px] text-slate-400 mb-2">
            <span className="flex items-center space-x-1">
              <MapPin className="w-3.5 h-3.5 text-sky-400" />
              <span>Spatial BBox Location (Page {field.page || 1}):</span>
            </span>
            <span className="font-mono text-[10px] text-sky-400">
              [{bbox.map((v) => v.toFixed(3)).join(', ')}]
            </span>
          </div>

          {/* Miniature Document Canvas Simulation */}
          <div className="relative w-full h-36 bg-slate-900 border border-slate-700/80 rounded shadow-inner overflow-hidden flex items-center justify-center">
            <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#94a3b8_1px,transparent_1px)] [background-size:12px_12px]" />
            <div
              className="absolute border-2 border-sky-400 bg-sky-500/25 rounded-sm transition-all animate-pulse"
              style={{
                left: `${bbox[0] * 100}%`,
                top: `${bbox[1] * 100}%`,
                width: `${Math.max(6, (bbox[2] - bbox[0]) * 100)}%`,
                height: `${Math.max(4, (bbox[3] - bbox[1]) * 100)}%`,
              }}
            >
              <span className="absolute -top-3 left-0 text-[8px] bg-sky-500 text-slate-950 font-bold px-1 rounded-xs">
                {fieldName}
              </span>
            </div>
            <span className="text-[10px] text-slate-600 font-mono">Page {field.page || 1} Canvas View</span>
          </div>
        </div>
      )}

      {/* Independent Grounding Tokens */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center space-x-1">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-semibold text-[11px]">Matched Evidence Tokens ({matchedTokens.length})</span>
          </span>
        </div>

        {matchedTokens.length > 0 ? (
          <div className="space-y-1 max-h-28 overflow-y-auto pr-1">
            {matchedTokens.map((t, idx) => (
              <div
                key={idx}
                className="text-[11px] font-mono bg-slate-950 p-2 rounded border border-slate-800 flex items-center justify-between text-slate-300"
              >
                <span className="truncate max-w-[180px]">&quot;{t.text}&quot;</span>
                <span className="text-[10px] text-indigo-400 uppercase bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                  {t.source}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-[11px] text-slate-500 italic bg-slate-950/40 p-2 rounded border border-slate-800/60">
            No exact matching independent tokens found in secondary layers.
          </div>
        )}
      </div>
    </div>
  );
}
