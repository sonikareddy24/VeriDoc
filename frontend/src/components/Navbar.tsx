import { Shield, FileCheck, FlaskConical, PlayCircle, Trash2, Cpu } from 'lucide-react';

interface NavbarProps {
  activeTab: 'workspace' | 'experiments';
  setActiveTab: (tab: 'workspace' | 'experiments') => void;
  onRunDemo: () => void;
  onClearSession: () => void;
  isAnalyzing: boolean;
  hasSession: boolean;
}

export default function Navbar({
  activeTab,
  setActiveTab,
  onRunDemo,
  onClearSession,
  isAnalyzing,
  hasSession,
}: NavbarProps) {
  return (
    <header className="border-b border-slate-800/80 bg-[#070b14]/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Tagline */}
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-sky-500 to-indigo-600 rounded-xl text-white shadow-lg shadow-sky-500/20">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-base text-white tracking-tight">VeriDocs AI</span>
              <span className="text-[10px] font-mono font-semibold tracking-wider uppercase px-2 py-0.5 bg-sky-500/15 border border-sky-500/30 text-sky-300 rounded-full">
                Evidence-First
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Financial Document Intelligence &amp; Fraud-Consistency</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1.5 bg-[#0b1120] p-1 rounded-xl border border-slate-800/80">
          <button
            onClick={() => setActiveTab('workspace')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
              activeTab === 'workspace'
                ? 'bg-gradient-to-r from-sky-500/20 to-blue-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <FileCheck className="w-4 h-4" />
            <span>Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('experiments')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
              activeTab === 'experiments'
                ? 'bg-gradient-to-r from-sky-500/20 to-blue-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <FlaskConical className="w-4 h-4" />
            <span>Benchmarks</span>
          </button>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <div className="hidden lg:flex items-center space-x-1.5 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded-md">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>CPU OCR Online</span>
          </div>

          <button
            onClick={onRunDemo}
            disabled={isAnalyzing}
            className="px-3.5 py-2 bg-gradient-to-r from-sky-500 via-blue-600 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-sky-500/25 transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            {isAnalyzing ? (
              <>
                <Cpu className="w-4 h-4 animate-spin text-sky-200" />
                <span>Running Pipeline...</span>
              </>
            ) : (
              <>
                <PlayCircle className="w-4 h-4" />
                <span>Run Live Demo</span>
              </>
            )}
          </button>

          {hasSession && (
            <button
              onClick={onClearSession}
              disabled={isAnalyzing}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all border border-slate-800 hover:border-rose-500/30"
              title="Clear Session & Purge Temp Storage"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
