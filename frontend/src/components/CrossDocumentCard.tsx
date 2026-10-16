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
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
            <GitCompare className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-xs font-semibold text-white tracking-tight">Cross-Document Reconciliation</h4>
              <span className="text-[10px] font-mono text-slate-400 bg-[#0B0F17] border border-slate-800 px-2 py-0.5 rounded">
                Multi-Entity Ledger
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Reconciles payroll disbursements against bank credits, clearing dates &amp; identity coherence
            </p>
          </div>
        </div>

        <span className="text-[11px] font-mono bg-[#0B0F17] border border-slate-800 text-slate-400 px-2.5 py-1 rounded-md">
          {findings.length} Multi-Entity Checks
        </span>
      </div>

      <div className="space-y-2.5">
        {findings.map((f, idx) => {
          const isSupported = f.status === 'Supported';
          const isInconsistent = f.status === 'Inconsistent';

          return (
            <div
              key={idx}
              className={`p-3.5 rounded-lg border text-xs transition-colors bg-[#161F30] ${
                isSupported
                  ? 'border-slate-800'
                  : isInconsistent
                  ? 'border-rose-900/60 bg-rose-950/10'
                  : 'border-amber-900/50 bg-amber-950/10'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div>
                  <h5 className="font-semibold text-slate-200 text-xs tracking-tight">{f.rule_name}</h5>
                  <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-mono mt-0.5">
                    <span className="text-blue-400 font-medium">{f.doc_name_a}</span>
                    <ArrowRightLeft className="w-3 h-3 text-slate-500" />
                    <span className="text-slate-300 font-medium">{f.doc_name_b}</span>
                  </div>
                </div>

                <span
                  className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold ${
                    isSupported
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/50'
                      : isInconsistent
                      ? 'bg-rose-950/60 text-rose-300 border border-rose-800/50'
                      : 'bg-amber-950/60 text-amber-300 border border-amber-800/50'
                  }`}
                >
                  {isSupported ? (
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  ) : isInconsistent ? (
                    <AlertTriangle className="w-3 h-3 text-rose-400" />
                  ) : (
                    <HelpCircle className="w-3 h-3 text-amber-400" />
                  )}
                  <span>{f.status}</span>
                </span>
              </div>

              <p className="text-[11px] text-slate-300 leading-relaxed font-normal">{f.explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
