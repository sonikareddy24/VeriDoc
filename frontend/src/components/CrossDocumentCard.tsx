import { GitCompare, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';
import { CrossDocumentFinding } from '../types';

interface CrossDocumentCardProps {
  findings: CrossDocumentFinding[];
}

export default function CrossDocumentCard({ findings }: CrossDocumentCardProps) {
  if (!findings || findings.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-indigo-400">
            <GitCompare className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Cross-Document Consistency Reconciliation</h4>
            <p className="text-xs text-slate-400">Deterministic multi-document cross-checks and timing reconciliation</p>
          </div>
        </div>

        <span className="text-xs font-mono bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 px-2 py-0.5 rounded">
          {findings.length} Multi-Document Rules
        </span>
      </div>

      <div className="space-y-3">
        {findings.map((f, idx) => {
          const isSupported = f.status === 'Supported';
          const isInconsistent = f.status === 'Inconsistent';

          return (
            <div
              key={idx}
              className={`p-3.5 rounded-lg border text-xs transition-all ${
                isSupported
                  ? 'bg-slate-950/60 border-slate-800/90 text-slate-300'
                  : isInconsistent
                  ? 'bg-rose-950/20 border-rose-500/40 text-rose-200'
                  : 'bg-amber-950/20 border-amber-500/40 text-amber-200'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div>
                  <h5 className="font-semibold text-slate-200 text-xs">{f.rule_name}</h5>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {f.doc_name_a} ↔ {f.doc_name_b}
                  </span>
                </div>

                <span
                  className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-[11px] font-semibold ${
                    isSupported
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : isInconsistent
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium'
                  }`}
                >
                  {isSupported ? (
                    <CheckCircle2 className="w-3 h-3" />
                  ) : isInconsistent ? (
                    <AlertTriangle className="w-3 h-3" />
                  ) : (
                    <HelpCircle className="w-3 h-3" />
                  )}
                  <span>{f.status}</span>
                </span>
              </div>

              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{f.explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
