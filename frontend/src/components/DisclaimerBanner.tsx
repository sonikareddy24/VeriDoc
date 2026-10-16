import { AlertCircle, ShieldAlert } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="bg-[#121826] border-b border-slate-800/90 px-4 py-2">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-2 text-slate-300">
          <ShieldAlert className="w-4 h-4 flex-shrink-0 text-amber-500" />
          <span className="font-semibold text-slate-200 uppercase tracking-wide text-[11px]">System Scope:</span>
          <span className="text-slate-400 font-normal">
            VeriDocs AI checks financial <strong className="text-slate-300 font-medium">consistency</strong> via deterministic arithmetic and independent OCR token evidence. It is a research prototype, not an authenticity or forensics verification system.
          </span>
        </div>
        <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] bg-[#1A2234] px-2.5 py-0.5 rounded border border-slate-700/60 font-mono">
          <AlertCircle className="w-3.5 h-3.5 text-slate-400" />
          <span>Local CPU operation • Zero external cloud calls</span>
        </div>
      </div>
    </div>
  );
}
