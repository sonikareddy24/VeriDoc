import { Shield, FileCheck, BarChart3, Play, Trash2, Cpu } from 'lucide-react';

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
    <header className="border-b border-slate-800 bg-[#0E131F] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Tagline */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-base text-white tracking-tight">VeriDocs AI</span>
              <span className="text-[11px] font-mono font-medium px-2 py-0.5 bg-slate-800 border border-slate-700/80 text-slate-300 rounded">
                Audit Engine
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal">
              Evidence-First Financial Verification &amp; Inconsistency Detection
            </p>
          </div>
        </div>

        {/* Navigation Tabs (Segmented control) */}
        <nav className="flex items-center bg-[#151C2C] p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab('workspace')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === 'workspace'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCheck className="w-3.5 h-3.5" />
            <span>Audit Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('experiments')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === 'experiments'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Benchmark Metrics</span>
          </button>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center space-x-3">
          <div className="hidden lg:flex items-center space-x-2 text-[11px] font-mono text-slate-400 bg-[#151C2C] border border-slate-800 px-2.5 py-1.2 rounded-md">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>CPU OCR • Ready</span>
          </div>

          <button
            onClick={onRunDemo}
            disabled={isAnalyzing}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center space-x-1.5 disabled:opacity-50"
          >
            {isAnalyzing ? (
              <>
                <Cpu className="w-3.5 h-3.5 animate-spin" />
                <span>Processing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Load Sample Scenario</span>
              </>
            )}
          </button>

          {hasSession && (
            <button
              onClick={onClearSession}
              disabled={isAnalyzing}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 rounded-lg transition-colors border border-slate-800"
              title="Reset Session"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
