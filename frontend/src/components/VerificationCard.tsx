import { CheckCircle2, XCircle, AlertCircle, ShieldAlert } from 'lucide-react';
import { VerificationCheck } from '../types';

interface VerificationCardProps {
  checks: VerificationCheck[];
}

export default function VerificationCard({ checks }: VerificationCardProps) {
  if (!checks || checks.length === 0) {
    return null;
  }

  const passedCount = checks.filter((c) => c.status === 'passed').length;
  const failedCount = checks.filter((c) => c.status === 'failed').length;
  const indetCount = checks.filter((c) => c.status === 'indeterminate').length;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Deterministic Verification Rules</h4>
            <p className="text-xs text-slate-400">Independent code checks, arithmetic validation & continuity</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {passedCount} Passed
          </span>
          {failedCount > 0 && (
            <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold">
              {failedCount} Discrepancies
            </span>
          )}
          {indetCount > 0 && (
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              {indetCount} N/A
            </span>
          )}
        </div>
      </div>

      <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
        {checks.map((chk) => {
          const isPassed = chk.status === 'passed';
          const isFailed = chk.status === 'failed';

          return (
            <div
              key={chk.check_id}
              className={`p-3 rounded-lg border text-xs transition-all ${
                isPassed
                  ? 'bg-slate-950/60 border-slate-800 text-slate-300'
                  : isFailed
                  ? 'bg-rose-950/20 border-rose-500/40 text-rose-200'
                  : 'bg-slate-950/30 border-slate-800/60 text-slate-500'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <span className="font-mono font-semibold text-[11px] text-slate-200">
                  {chk.check_id}
                </span>
                <span
                  className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                    isPassed
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : isFailed
                      ? 'bg-rose-500/20 text-rose-400 font-bold'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {isPassed ? <CheckCircle2 className="w-3 h-3" /> : isFailed ? <XCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                  <span>{chk.status}</span>
                </span>
              </div>
              <p className="text-[11px] leading-relaxed text-slate-300">{chk.plain_explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
