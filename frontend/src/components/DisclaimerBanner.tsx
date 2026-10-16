import { AlertTriangle, Info } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-slate-900 border-y border-amber-500/20 px-4 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-2 text-amber-300">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-400" />
          <span className="font-semibold tracking-wide uppercase text-[11px]">Research Prototype Disclaimer:</span>
          <span className="text-amber-200/90 font-normal">
            VeriDocs AI checks financial consistency via deterministic evidence. It is NOT an authenticity, forensics, or fraud verification system.
          </span>
        </div>
        <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] bg-slate-800/60 px-2.5 py-1 rounded border border-slate-700/50">
          <Info className="w-3.5 h-3.5 text-sky-400" />
          <span>Do not upload real sensitive financial documents.</span>
        </div>
      </div>
    </div>
  );
}
