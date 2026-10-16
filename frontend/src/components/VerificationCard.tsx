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
    if (id.includes('ARITHMETIC') || id.includes('TOTAL') || id.includes('SUM') || id.includes('BALANCE')) {
      return <Calculator className="w-4 h-4 text-blue-400" />;
    }
    if (id.includes('PERIOD') || id.includes('DATE') || id.includes('CHRONOLOGY')) {
      return <Calendar className="w-4 h-4 text-slate-400" />;
    }
    if (id.includes('HYGIENE') || id.includes('INJECTION')) {
      return <Sparkles className="w-4 h-4 text-amber-400" />;
    }
    return <Layers className="w-4 h-4 text-emerald-400" />;
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-xs font-semibold text-white tracking-tight">Deterministic Invariant Audits</h4>
              <span className="text-[10px] font-mono text-slate-400 bg-[#0B0F17] border border-slate-800 px-2 py-0.5 rounded">
                Independent Python Rules Engine
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Mathematical formulas, balance chaining &amp; plausibility rules executed outside AI model
            </p>
          </div>
        </div>

        {/* Filter Pills & Collapse */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 bg-[#0B0F17] p-1 rounded-lg border border-slate-800 text-[11px]">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                filter === 'ALL' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({checks.length})
            </button>
            <button
              onClick={() => setFilter('passed')}
              className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                filter === 'passed' ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-800/60' : 'text-emerald-500 hover:text-emerald-400'
              }`}
            >
              {passedCount} Passed
            </button>
            {failedCount > 0 && (
              <button
                onClick={() => setFilter('failed')}
                className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                  filter === 'failed' ? 'bg-rose-950/70 text-rose-300 border border-rose-800/60' : 'text-rose-500 hover:text-rose-400'
                }`}
              >
                {failedCount} Inconsistent
              </button>
            )}
            {indetCount > 0 && (
              <button
                onClick={() => setFilter('indeterminate')}
                className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                  filter === 'indeterminate' ? 'bg-amber-950/70 text-amber-300 border border-amber-800/60' : 'text-amber-500 hover:text-amber-400'
                }`}
              >
                {indetCount} Uncertain
              </button>
            )}
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors"
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Rules Grid */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {filteredChecks.map((check, idx) => {
            const isPassed = check.status === 'passed';
            const isFailed = check.status === 'failed';

            return (
              <div
                key={idx}
                className={`p-3.5 rounded-lg border text-xs transition-colors space-y-2 bg-[#161F30] ${
                  isPassed
                    ? 'border-slate-800'
                    : isFailed
                    ? 'border-rose-900/60 bg-rose-950/10'
                    : 'border-slate-800/80'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <div className="p-1.5 bg-[#111827] rounded border border-slate-800">
                      {getCheckIcon(check.check_id)}
                    </div>
                    <div>
                      <div className="font-mono text-[11px] font-semibold text-slate-200">
                        {check.check_id}
                      </div>
                      <div className="text-[10px] text-slate-400 capitalize font-mono">
                        {check.independence} verification
                      </div>
                    </div>
                  </div>

                  {isPassed ? (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-800/50">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      <span>PASSED</span>
                    </span>
                  ) : isFailed ? (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-950/60 text-rose-300 border border-rose-800/50">
                      <XCircle className="w-3 h-3 text-rose-400" />
                      <span>FAILED</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-950/60 text-amber-300 border border-amber-800/50">
                      <AlertCircle className="w-3 h-3 text-amber-400" />
                      <span>UNCERTAIN</span>
                    </span>
                  )}
                </div>

                <p className="text-[11px] text-slate-300 leading-relaxed font-normal">
                  {check.plain_explanation}
                </p>

                {check.evidence_refs && check.evidence_refs.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1 pt-0.5">
                    <span className="text-[10px] text-slate-500 font-mono">Evidence:</span>
                    {check.evidence_refs.map((ref, rIdx) => (
                      <span
                        key={rIdx}
                        className="font-mono text-[10px] bg-[#0B0F17] px-1.5 py-0.5 rounded border border-slate-800 text-slate-400"
                      >
                        {ref}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
