import { Shield, FileCheck, FlaskConical, PlayCircle, Trash2 } from 'lucide-react';

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
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-xl text-sky-400">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">VeriDocs AI</span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 bg-sky-500/15 border border-sky-500/30 text-sky-300 rounded-full">
                Evidence-First
              </span>
            </div>
            <p className="text-xs text-slate-400">Financial Document Consistency Intelligence</p>
          </div>
        </div>

        <nav className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('workspace')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === 'workspace'
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FileCheck className="w-4 h-4" />
            <span>Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('experiments')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === 'experiments'
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FlaskConical className="w-4 h-4" />
            <span>Research Benchmarks</span>
          </button>
        </nav>

        <div className="flex items-center space-x-3">
          <button
            onClick={onRunDemo}
            disabled={isAnalyzing}
            className="px-3 py-1.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white rounded-lg text-xs font-medium shadow-md shadow-sky-500/20 transition-all flex items-center space-x-1.5 disabled:opacity-50"
          >
            <PlayCircle className="w-4 h-4" />
            <span>{isAnalyzing ? 'Analyzing...' : 'Run Live Demo'}</span>
          </button>

          {hasSession && (
            <button
              onClick={onClearSession}
              disabled={isAnalyzing}
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all border border-transparent hover:border-rose-500/20"
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
