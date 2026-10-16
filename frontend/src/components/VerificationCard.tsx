import { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Calculator,
  Calendar,
  Layers,
  Sparkles,
} from 'lucide-react';
import { VerificationCheck } from '../types';

interface VerificationCardProps {
  checks: VerificationCheck[];
}

export default function VerificationCard({ checks }: VerificationCardProps) {
  const [filter, setFilter] = useState<'ALL' | 'passed' | 'failed' | 'indeterminate'>('ALL');
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  if (!checks || checks.length === 0) {
    return null;
  }

  const passedCount = checks.filter((c) => c.status === 'passed').length;
  const failedCount = checks.filter((c) => c.status === 'failed').length;
  const indetCount = checks.filter((c) => c.status === 'indeterminate').length;

  const filteredChecks = checks.filter((c) => filter === 'ALL' || c.status === filter);

  const getCheckIcon = (id: string) => {
    if (id.includes('ARITHMETIC') || id.includes('TOTAL') || id.includes('SUM')) {
      return <Calculator className="w-4 h-4 text-sky-400" />;
    }
    if (id.includes('PERIOD') || id.includes('DATE') || id.includes('CHRONOLOGY')) {
      return <Calendar className="w-4 h-4 text-indigo-400" />;
    }
    if (id.includes('HYGIENE')) {
      return <Sparkles className="w-4 h-4 text-amber-400" />;
    }
    return <Layers className="w-4 h-4 text-emerald-400" />;
  };

  return (
    <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl p-5 shadow-2xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/30 rounded-xl text-blue-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-sm font-bold text-white tracking-tight">Deterministic Invariant Audits</h4>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                Independent Engine
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Mathematical formulas, balance chaining &amp; plausibility rules executed outside AI
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Status Counter Pills */}
          <div className="flex items-center space-x-1.5 text-xs font-mono">
            <button
              onClick={() => setFilter(filter === 'passed' ? 'ALL' : 'passed')}
              className={`px-2 py-0.5 rounded-md font-semibold transition-all ${
                filter === 'passed'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/15'
              }`}
            >
              {passedCount} Passed
            </button>

            {failedCount > 0 && (
              <button
                onClick={() => setFilter(filter === 'failed' ? 'ALL' : 'failed')}
                className={`px-2 py-0.5 rounded-md font-bold transition-all ${
                  filter === 'failed'
                    ? 'bg-rose-500/30 text-rose-300 border border-rose-500/50'
                    : 'bg-rose-500/15 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20'
                }`}
              >
                {failedCount} Inconsistent
              </button>
            )}

            {indetCount > 0 && (
              <button
                onClick={() => setFilter(filter === 'indeterminate' ? 'ALL' : 'indeterminate')}
                className="px-2 py-0.5 rounded-md text-slate-400 bg-slate-900 border border-slate-800 hover:text-slate-200"
              >
                {indetCount} N/A
              </button>
            )}
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-all ml-1"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
          {filteredChecks.map((chk) => {
            const isPassed = chk.status === 'passed';
            const isFailed = chk.status === 'failed';

            return (
              <div
                key={chk.check_id}
                className={`p-3.5 rounded-xl border text-xs transition-all ${
                  isPassed
                    ? 'bg-[#070b14]/80 border-slate-800/80 hover:border-slate-700/80 text-slate-300'
                    : isFailed
                    ? 'bg-rose-950/20 border-rose-500/40 text-rose-200 shadow-glow-rose'
                    : 'bg-[#070b14]/40 border-slate-800/50 text-slate-500'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center space-x-2">
                    {getCheckIcon(chk.check_id)}
                    <span className="font-mono font-semibold text-[11px] text-slate-200">
                      {chk.check_id}
                    </span>
                  </div>

                  <span
                    className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                      isPassed
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : isFailed
                        ? 'bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {isPassed ? (
                      <CheckCircle2 className="w-3 h-3" />
                    ) : isFailed ? (
                      <XCircle className="w-3 h-3" />
                    ) : (
                      <AlertCircle className="w-3 h-3" />
                    )}
                    <span>{chk.status}</span>
                  </span>
                </div>

                <p className="text-[11px] leading-relaxed text-slate-300 font-sans pl-6">
                  {chk.plain_explanation}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
