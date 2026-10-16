import { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertCircle,
  Search,
  Copy,
  Check,
  Filter,
} from 'lucide-react';
import { ExtractedField, FieldStatus } from '../types';

interface FieldTableProps {
  fields: Record<string, ExtractedField>;
  selectedField: string | null;
  onSelectField: (fieldName: string) => void;
}

export default function FieldTable({ fields, selectedField, onSelectField }: FieldTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleCopy = (e: React.MouseEvent, name: string, val: any) => {
    e.stopPropagation();
    navigator.clipboard.writeText(String(val ?? ''));
    setCopiedField(name);
    setTimeout(() => setCopiedField(null), 1800);
  };

  const getStatusBadge = (status: FieldStatus) => {
    switch (status) {
      case 'Supported':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            <span>Supported</span>
          </span>
        );
      case 'Inconsistent':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3 h-3" />
            <span>Inconsistent</span>
          </span>
        );
      case 'Uncertain':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <HelpCircle className="w-3 h-3" />
            <span>Uncertain</span>
          </span>
        );
      case 'Unreadable':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wide bg-slate-800 text-slate-400 border border-slate-700">
            <AlertCircle className="w-3 h-3" />
            <span>Unreadable</span>
          </span>
        );
    }
  };

  const fieldEntries = Object.entries(fields);

  // Filter entries
  const filteredEntries = fieldEntries.filter(([name, f]) => {
    const matchesSearch =
      name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(f.value ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(f.normalized_value ?? '').toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'ALL' || f.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const countByStatus = {
    Supported: fieldEntries.filter(([_, f]) => f.status === 'Supported').length,
    Inconsistent: fieldEntries.filter(([_, f]) => f.status === 'Inconsistent').length,
    Uncertain: fieldEntries.filter(([_, f]) => f.status === 'Uncertain').length,
    Unreadable: fieldEntries.filter(([_, f]) => f.status === 'Unreadable').length,
  };

  return (
    <div className="bg-[#0b1120]/90 backdrop-blur-md border border-slate-800/80 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
      {/* Table Header & Controls */}
      <div className="p-4 border-b border-slate-800/80 bg-[#0d1629]/90 space-y-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">Extracted Semantic Ledger</h3>
            <p className="text-xs text-slate-400">
              Normalized fields grounded against OCR token coordinates &amp; arithmetic rules
            </p>
          </div>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
            {filteredEntries.length} of {fieldEntries.length} Fields
          </span>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search field or value..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/60 focus:ring-1 focus:ring-sky-500/30 transition-all font-sans"
            />
          </div>

          <div className="flex items-center space-x-1 text-[11px]">
            <Filter className="w-3.5 h-3.5 text-slate-500 mr-1" />
            {['ALL', 'Supported', 'Inconsistent', 'Uncertain', 'Unreadable'].map((st) => {
              const active = statusFilter === st;
              const count = st === 'ALL' ? fieldEntries.length : countByStatus[st as keyof typeof countByStatus] || 0;

              return (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2 py-1 rounded-md font-medium transition-all ${
                    active
                      ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <span>{st}</span>
                  <span className="ml-1 text-[10px] opacity-75 font-mono">({count})</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto max-h-[440px] overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#090e1a]/90 text-slate-400 font-semibold border-b border-slate-800/80 sticky top-0 backdrop-blur-md z-10 text-[11px] uppercase tracking-wider font-mono">
            <tr>
              <th className="py-2.5 px-4 font-sans">Field Identifier</th>
              <th className="py-2.5 px-4">Raw Extracted</th>
              <th className="py-2.5 px-4">Normalized Value</th>
              <th className="py-2.5 px-4">Verification Status</th>
              <th className="py-2.5 px-4">Engine / Confidence</th>
              <th className="py-2.5 px-4 text-right font-sans">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 font-mono text-slate-300 text-xs">
            {filteredEntries.map(([name, field]) => {
              const isSelected = selectedField === name;
              const displayVal = field.value !== null && field.value !== undefined ? String(field.value) : '—';
              const normVal =
                field.normalized_value !== null && field.normalized_value !== undefined
                  ? String(field.normalized_value)
                  : '—';

              return (
                <tr
                  key={name}
                  onClick={() => onSelectField(name)}
                  className={`cursor-pointer transition-all duration-150 relative ${
                    isSelected
                      ? 'bg-sky-500/15 text-white shadow-inner border-l-2 border-l-sky-400'
                      : 'hover:bg-slate-800/30'
                  }`}
                >
                  <td className="py-3 px-4 font-sans font-semibold text-slate-200 capitalize">
                    {name.replace(/_/g, ' ')}
                  </td>
                  <td className="py-3 px-4 truncate max-w-[150px] text-slate-400 font-normal" title={displayVal}>
                    {displayVal}
                  </td>
                  <td className="py-3 px-4 text-sky-400 font-bold truncate max-w-[160px]" title={normVal}>
                    {normVal}
                  </td>
                  <td className="py-3 px-4 font-sans">
                    {getStatusBadge(field.status)}
                  </td>
                  <td className="py-3 px-4 text-[11px] text-slate-400 font-sans">
                    <div className="font-mono text-[10px] text-slate-300">{field.extractor}</div>
                    {field.ocr_confidence !== undefined && field.ocr_confidence !== null && (
                      <div className="text-[10px] text-slate-500 font-mono">
                        OCR Conf: <span className="text-slate-300">{(field.ocr_confidence * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right font-sans">
                    <button
                      onClick={(e) => handleCopy(e, name, normVal !== '—' ? normVal : displayVal)}
                      className="p-1.5 text-slate-400 hover:text-sky-300 hover:bg-slate-800 rounded-md transition-all"
                      title="Copy value"
                    >
                      {copiedField === name ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
