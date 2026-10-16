import { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertCircle,
  Search,
  Copy,
  Check,
  Table as TableIcon,
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
    setTimeout(() => setCopiedField(null), 1500);
  };

  const getStatusBadge = (status: FieldStatus) => {
    switch (status) {
      case 'Supported':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-950/60 text-emerald-300 border border-emerald-800/50">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Supported</span>
          </span>
        );
      case 'Inconsistent':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium bg-rose-950/60 text-rose-300 border border-rose-800/50">
            <XCircle className="w-3 h-3 text-rose-400" />
            <span>Inconsistent</span>
          </span>
        );
      case 'Uncertain':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium bg-amber-950/60 text-amber-300 border border-amber-800/50">
            <HelpCircle className="w-3 h-3 text-amber-400" />
            <span>Uncertain</span>
          </span>
        );
      case 'Unreadable':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
            <AlertCircle className="w-3 h-3 text-slate-400" />
            <span>Unreadable</span>
          </span>
        );
    }
  };

  const fieldEntries = Object.entries(fields);

  // Status Counts
  const counts = {
    ALL: fieldEntries.length,
    Supported: fieldEntries.filter(([_, f]) => f.status === 'Supported').length,
    Inconsistent: fieldEntries.filter(([_, f]) => f.status === 'Inconsistent').length,
    Uncertain: fieldEntries.filter(([_, f]) => f.status === 'Uncertain').length,
    Unreadable: fieldEntries.filter(([_, f]) => f.status === 'Unreadable').length,
  };

  // Filtered List
  const filteredFields = fieldEntries.filter(([name, field]) => {
    const matchesSearch =
      name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(field.value ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(field.normalized_value ?? '').toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'ALL' || field.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
      {/* Table Header / Filter Bar */}
      <div className="p-4 bg-[#161F30] border-b border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-md bg-slate-800 flex items-center justify-center text-slate-300">
              <TableIcon className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h3 className="text-xs font-semibold text-white tracking-tight">Extracted Semantic Ledger</h3>
              <p className="text-[11px] text-slate-400">
                Ground-truth scalar values cross-checked with OCR tokens
              </p>
            </div>
          </div>
          <span className="text-[11px] font-mono text-slate-400 bg-[#111827] px-2 py-0.5 rounded border border-slate-800">
            {fieldEntries.length} Fields
          </span>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search field identifier or extracted value..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-[#0B0F17] border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-hidden focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Status Filter Badges */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          {(['ALL', 'Supported', 'Inconsistent', 'Uncertain', 'Unreadable'] as const).map((st) => {
            const count = counts[st];
            if (count === 0 && st !== 'ALL') return null;
            const isSelected = statusFilter === st;

            return (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors flex items-center space-x-1 border ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-500'
                    : 'bg-[#0B0F17] text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <span>{st === 'ALL' ? 'All' : st}</span>
                <span className={`px-1 rounded text-[9px] font-mono ${isSelected ? 'bg-blue-700 text-white' : 'bg-slate-800 text-slate-400'}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Table Data */}
      <div className="overflow-x-auto max-h-[420px] overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-[#0E1422] text-[10px] font-semibold text-slate-400 uppercase tracking-wider sticky top-0 z-10">
              <th className="py-2 px-3">Field</th>
              <th className="py-2 px-3">Raw Extracted</th>
              <th className="py-2 px-3">Normalized</th>
              <th className="py-2 px-3 text-right">Confidence</th>
              <th className="py-2 px-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {filteredFields.length > 0 ? (
              filteredFields.map(([name, field]) => {
                const isSelected = selectedField === name;

                return (
                  <tr
                    key={name}
                    onClick={() => onSelectField(name)}
                    className={`cursor-pointer transition-colors group ${
                      isSelected
                        ? 'bg-blue-950/25 border-l-2 border-l-blue-500 text-white'
                        : 'hover:bg-slate-850/40 text-slate-300'
                    }`}
                  >
                    <td className="py-2.5 px-3">
                      <div className="font-mono text-[11px] font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                        {name}
                      </div>
                    </td>
                    <td className="py-2.5 px-3 max-w-[160px]">
                      <div className="flex items-center space-x-1.5">
                        <span className="truncate text-slate-300 font-mono text-[11px]">
                          {String(field.value ?? '—')}
                        </span>
                        {field.value !== null && field.value !== undefined && (
                          <button
                            onClick={(e) => handleCopy(e, name, field.value)}
                            className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-slate-200 transition-opacity"
                            title="Copy Value"
                          >
                            {copiedField === name ? (
                              <Check className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                        )}
                      </div>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400 max-w-[140px] truncate">
                      {field.normalized_value !== null && field.normalized_value !== undefined
                        ? String(field.normalized_value)
                        : '—'}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-right text-slate-400">
                      {field.ocr_confidence !== null && field.ocr_confidence !== undefined
                        ? `${(field.ocr_confidence * 100).toFixed(1)}%`
                        : '—'}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      {getStatusBadge(field.status)}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={5} className="py-8 text-center text-xs text-slate-500">
                  No matching fields found for "{searchTerm}".
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
