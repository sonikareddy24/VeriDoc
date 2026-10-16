import { GitCompare, CheckCircle2, AlertTriangle, HelpCircle, ArrowRightLeft } from 'lucide-react';
import { CrossDocumentFinding } from '../types';

interface CrossDocumentCardProps {
  findings: CrossDocumentFinding[];
}

export default function CrossDocumentCard({ findings }: CrossDocumentCardProps) {
  if (!findings || findings.length === 0) {
    return null;
  }

  return (
    <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl p-5 shadow-2xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-indigo-500/20 to-purple-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
            <GitCompare className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-sm font-bold text-white tracking-tight">Cross-Document Financial Reconciliation</h4>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 font-semibold">
                Multi-Document Invariants
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Reconciles payroll disbursements against bank statement transaction credits &amp; clearing dates
            </p>
          </div>
        </div>

        <span className="text-xs font-mono bg-slate-900 border border-slate-800 text-slate-400 px-2.5 py-1 rounded-lg">
          {findings.length} Multi-Entity Checks
        </span>
      </div>

      <div className="space-y-3">
        {findings.map((f, idx) => {
          const isSupported = f.status === 'Supported';
          const isInconsistent = f.status === 'Inconsistent';

          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border text-xs transition-all ${
                isSupported
                  ? 'bg-[#070b14]/80 border-slate-800/80 text-slate-300'
                  : isInconsistent
                  ? 'bg-rose-950/20 border-rose-500/40 text-rose-200 shadow-glow-rose'
                  : 'bg-amber-950/20 border-amber-500/40 text-amber-200'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <h5 className="font-bold text-slate-100 text-xs tracking-tight">{f.rule_name}</h5>
                  <div className="flex items-center space-x-1.5 text-[11px] text-slate-400 font-mono mt-0.5">
                    <span className="text-sky-300">{f.doc_name_a}</span>
                    <ArrowRightLeft className="w-3 h-3 text-slate-500" />
                    <span className="text-indigo-300">{f.doc_name_b}</span>
                  </div>
                </div>

                <span
                  className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                    isSupported
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      : isInconsistent
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
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
